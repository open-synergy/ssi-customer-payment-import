# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import csv
import hashlib
import io
import json

import openpyxl

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.ssi_decorator import ssi_decorator


class CustomerPaymentImport(models.Model):  # pylint: disable=too-few-public-methods
    """
    Transactional document for importing customer payment transactions from
    a bank file (CSV or XLSX). Reads the file into raw data lines, then
    creates the resulting Customer Payments via queue jobs.

    Lifecycle: draft -> confirm -> queue_done -> done
    Cancellation: queue_cancel -> cancel
    """

    _name = "customer_payment_import"
    _description = "Customer Payment Import"
    _inherit = [
        "mixin.transaction_queue_cancel",
        "mixin.transaction_queue_done",
        "mixin.transaction_confirm",
        "mixin.many2one_configurator",
    ]

    # Multiple Approval Attribute
    _approval_from_state = "draft"
    _approval_to_state = "action_queue_done"
    _approval_state = "confirm"
    _after_approved_method = "action_queue_done"

    # View auto-insert attributes
    _automatically_insert_view_element = True
    _automatically_insert_multiple_approval_page = True
    _automatically_insert_done_policy_fields = False
    _automatically_insert_done_button = False
    _queue_processing_create_page = True
    _automatically_insert_queue_done_button = False
    _automatically_insert_queue_cancel_button = False

    _queue_to_done_insert_form_element_ok = True
    _queue_to_done_form_xpath = "//group[@name='queue_processing']"

    _queue_to_cancel_insert_form_element_ok = True
    _queue_to_cancel_form_xpath = "//group[@name='queue_processing']"

    _method_to_run_from_wizard = "action_queue_cancel"

    _statusbar_visible_label = "draft,confirm,queue_done,done"

    _policy_field_order = [
        "confirm_ok",
        "approve_ok",
        "reject_ok",
        "restart_approval_ok",
        "queue_cancel_ok",
        "cancel_ok",
        "restart_ok",
        "done_ok",
        "queue_done_ok",
        "manual_number_ok",
    ]
    _header_button_order = [
        "action_confirm",
        "action_approve_approval",
        "action_reject_approval",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "action_restart",
    ]

    # Attributes related to add element on search view automatically
    _state_filter_order = [
        "dom_draft",
        "dom_confirm",
        "dom_reject",
        "dom_queue_done",
        "dom_done",
        "dom_terminate",
        "dom_queue_cancel",
        "dom_cancel",
    ]

    # Sequence attribute
    _create_sequence_state = "done"

    date = fields.Date(
        string="Date",
        required=True,
        default=lambda self: fields.Date.today(),
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Date of this import document.",
    )
    type_id = fields.Many2one(
        string="Type",
        comodel_name="customer_payment_import_type",
        required=True,
        ondelete="restrict",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help=(
            "Import type that determines the file format, column mapping, "
            "and allowed journals for this document."
        ),
    )
    allowed_journal_ids = fields.Many2many(
        string="Allowed Journals",
        comodel_name="account.journal",
        compute="_compute_allowed_journal_ids",
        store=False,
        compute_sudo=True,
        help="Journals allowed to be selected, as configured on the Type.",
    )
    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
        required=True,
        ondelete="restrict",
        readonly=True,
        states={"draft": [("readonly", False)]},
        domain="[('id', 'in', allowed_journal_ids)]",
        help="Journal used to create the customer payments from this import.",
    )
    import_file = fields.Binary(
        string="Import File",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="The bank payment file to import, in the format defined by Type.",
    )
    import_file_name = fields.Char(
        string="File Name",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Original file name of the uploaded import file.",
    )
    import_file_hash = fields.Char(
        string="File Hash",
        readonly=True,
        copy=False,
        help=(
            "SHA-256 hash of the uploaded import file. Used to detect "
            "duplicate imports."
        ),
    )
    data_ids = fields.One2many(
        string="Import Data",
        comodel_name="customer_payment_import.data",
        inverse_name="import_id",
        readonly=True,
        states={"queue_done": [("readonly", False)]},
        help="Raw rows read from the import file, one record per row.",
    )

    @api.depends("type_id")
    def _compute_allowed_journal_ids(self):
        for record in self:
            result = False
            if record.type_id:
                result = record._m2o_configurator_get_filter(
                    object_name="account.journal",
                    method_selection=record.type_id.journal_selection_method,
                    manual_recordset=record.type_id.journal_ids,
                    domain=record.type_id.journal_domain,
                    python_code=record.type_id.journal_python_code,
                )
            record.allowed_journal_ids = result

    @api.constrains("import_file_hash")
    def _check_duplicate_import_file_hash(self):
        for document in self.sudo():
            if not document._check_duplicate_import_file_hash_condition():
                error_message = """
Context: Uploading customer payment import file
Document: %s
Problem: This file has already been imported by another document
Solution: Check the existing import or use a different file""" % (
                    document.name or str(document.id)
                )
                raise ValidationError(_(error_message))

    def _check_duplicate_import_file_hash_condition(self):
        self.ensure_one()
        if not self.import_file_hash:
            return True
        duplicate = self.search(
            [
                ("import_file_hash", "=", self.import_file_hash),
                ("id", "!=", self.id),
                ("state", "!=", "cancel"),
            ],
            limit=1,
        )
        return not duplicate

    def action_load_data(self):
        for record in self.sudo():
            record._load_data()

    def _load_data(self):
        self.ensure_one()

        if self.data_ids:
            self.data_ids.unlink()

        if not self.import_file:
            return

        file_content = base64.b64decode(self.import_file)
        self.import_file_hash = hashlib.sha256(file_content).hexdigest()

        rows = self._read_rows(file_content)
        data_vals = []
        for sequence, row in enumerate(rows, start=1):
            data_vals.append(self._prepare_import_data(sequence, row))

        if data_vals:
            self.env["customer_payment_import.data"].create(data_vals)

    def _prepare_import_data(self, sequence, row):
        self.ensure_one()
        return {
            "import_id": self.id,
            "sequence": sequence,
            "data": json.dumps(row, default=str),
        }

    def _read_rows(self, file_content):
        """
        Return a list of row dicts (header/index -> value) read from
        ``file_content``, honoring the Type's offset_row, no_header, and
        skip_empty_lines settings.
        """
        self.ensure_one()
        ctype = self.type_id

        if ctype.file_type == "xlsx":
            raw_rows = self._iter_raw_rows_xlsx(file_content)
        else:
            raw_rows = self._iter_raw_rows_csv(file_content)

        rows = []
        headers = None
        for index, raw_row in enumerate(raw_rows):
            if index < ctype.offset_row:
                continue
            if ctype.skip_empty_lines and not any(
                str(cell).strip() for cell in raw_row
            ):
                continue
            if not ctype.no_header and headers is None:
                headers = [str(cell) for cell in raw_row]
                continue
            if headers:
                row_dict = dict(zip(headers, raw_row))
            else:
                row_dict = {str(i): value for i, value in enumerate(raw_row)}
            rows.append(row_dict)
        return rows

    def _iter_raw_rows_csv(self, file_content):
        """Yield each row (list of cell strings) of a CSV import file."""
        self.ensure_one()
        ctype = self.type_id
        encoding = ctype.file_encoding or "utf-8"
        content_str = file_content.decode(encoding)
        delimiter = ctype._get_column_delimiter_character()
        quotechar = ctype.quotechar or '"'
        lines_io = io.StringIO(content_str)
        reader = csv.reader(lines_io, delimiter=delimiter, quotechar=quotechar)
        for row in reader:
            yield list(row)

    def _iter_raw_rows_xlsx(self, file_content):
        """Yield each row (list of cell values) of an XLSX import file."""
        self.ensure_one()
        ctype = self.type_id
        workbook = openpyxl.load_workbook(
            io.BytesIO(file_content), read_only=True, data_only=True
        )
        sheet = workbook[ctype.sheet_name] if ctype.sheet_name else workbook.active
        for row in sheet.iter_rows(values_only=True):
            yield ["" if cell is None else cell for cell in row]

    @ssi_decorator.post_queue_done_action()
    def _01_create_payment_on_queue_done(self):
        self.ensure_one()
        for data_line in self.data_ids:
            description = "Create customer payment for data line ID %s" % data_line.id
            data_line.with_context(job_batch=self.done_queue_job_batch_id).with_delay(
                description=_(description)
            )._process_payment()

    @ssi_decorator.post_queue_cancel_action()
    def _01_cancel_payment_on_queue_cancel(self):
        self.ensure_one()
        for data_line in self.data_ids.filtered(lambda d: d.payment_id):
            description = "Cancel customer payment for data line ID %s" % data_line.id
            data_line.with_context(job_batch=self.cancel_queue_job_batch_id).with_delay(
                description=_(description)
            )._cancel_payment()

    @ssi_decorator.insert_on_form_view()
    def _insert_form_element(self, view_arch):
        if self._automatically_insert_view_element:
            view_arch = self._reconfigure_statusbar_visible(view_arch)
        return view_arch

    @api.model
    def _get_policy_field(self):
        res = super()._get_policy_field()
        policy_field = [
            "confirm_ok",
            "approve_ok",
            "reject_ok",
            "restart_approval_ok",
            "queue_done_ok",
            "queue_cancel_ok",
            "done_ok",
            "cancel_ok",
            "restart_ok",
            "manual_number_ok",
        ]
        res += policy_field
        return res
