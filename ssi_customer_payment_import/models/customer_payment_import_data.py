# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from datetime import datetime

from odoo import _, api, fields, models, registry
from odoo.exceptions import UserError

from odoo.addons.base.models.res_bank import sanitize_account_number


class CustomerPaymentImportData(models.Model):  # pylint: disable=too-few-public-methods
    """
    One line per row of the customer payment import file. Stores the raw
    row as JSON and tracks the resulting account.payment record created
    from it.
    """

    _name = "customer_payment_import.data"
    _description = "Customer Payment Import - Data"
    _order = "import_id, sequence"

    import_id = fields.Many2one(
        string="# Import",
        comodel_name="customer_payment_import",
        required=True,
        ondelete="cascade",
        help="The import document this line belongs to.",
    )
    sequence = fields.Integer(
        string="Sequence",
        required=True,
        default=5,
        help="Row sequence from the source file.",
    )
    data = fields.Text(
        string="Data",
        help="Raw row data from the import file, stored as a JSON object.",
    )
    payment_id = fields.Many2one(
        string="Payment",
        comodel_name="account.payment",
        ondelete="set null",
        copy=False,
        help="The customer payment created from this data line.",
    )
    state = fields.Selection(
        string="Status",
        selection=[
            ("draft", "Draft"),
            ("done", "Done"),
            ("error", "Error"),
            ("ignored", "Ignored"),
        ],
        default="draft",
        required=True,
        readonly=True,
        copy=False,
        help="Processing status of this data line.",
    )
    error_message = fields.Text(
        string="Error Message",
        readonly=True,
        copy=False,
        help="Reason why this data line failed to be converted into a "
        "customer payment.",
    )
    ignore_reason = fields.Text(
        string="Ignore Reason",
        copy=False,
        help="Reason why this data line is excluded from the import.",
    )
    queue_job_id = fields.Many2one(
        string="Queue Job",
        comodel_name="queue.job",
        readonly=True,
        ondelete="set null",
        copy=False,
        help="Queue job that processes this data line.",
    )
    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
        related="payment_id.partner_id",
        store=True,
        compute_sudo=True,
        help="Customer derived from the linked payment record.",
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        related="payment_id.currency_id",
        store=True,
        compute_sudo=True,
        help="Currency of the linked payment record.",
    )
    amount = fields.Monetary(
        string="Amount",
        related="payment_id.amount",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help="Amount of the linked payment record.",
    )

    def _get_row_data(self):
        """Decode ``data`` (raw JSON row) into a plain dict.

        :return: dict of column name/index to cell value; empty dict
            when ``data`` is empty or not valid JSON
        """
        self.ensure_one()
        if not self.data:
            return {}
        try:
            return json.loads(self.data)
        except (ValueError, TypeError):
            return {}

    def _get_type(self):
        """Return the import Type of this line's parent document.

        :return: ``customer_payment_import_type`` record
        """
        self.ensure_one()
        return self.import_id.type_id

    # -------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------

    def _find_partner_by_bank_account(self, acc_number):
        """Return the res.partner owning the res.partner.bank matching
        ``acc_number`` (compared after sanitization), or an empty recordset."""
        self.ensure_one()
        sanitized = sanitize_account_number(str(acc_number or ""))
        if not sanitized:
            return self.env["res.partner"]
        bank = self.env["res.partner.bank"].search(
            [("sanitized_acc_number", "=", sanitized)], limit=1
        )
        return bank.partner_id

    def _parse_amount(self, value):
        """Parse ``value`` (number or string, possibly with thousands/decimal
        separators) into a float. Raise UserError if it cannot be parsed.

        A numeric ``value`` (``int``/``float``, as read from an XLSX
        cell) is returned as-is and never goes through the import
        Type's amount format normalization. A string ``value`` is
        first normalized by the import Type's
        ``_normalize_amount_text`` -- which applies the configured
        Amount Format (``auto``/``manual``) and separators -- before
        being converted with ``float()``.
        """
        self.ensure_one()
        if isinstance(value, (int, float)):
            return float(value)

        ctype = self._get_type()
        text = ctype._normalize_amount_text(value)

        try:
            return float(text)
        except ValueError as error:
            raise UserError(
                _(
                    """
Context: Processing customer payment import data line
Document: %s (sequence %s)
Problem: Could not parse amount value '%s' under Amount Format '%s'
         (Amount Thousand Separator '%s', Amount Decimal Separator
         '%s')
Solution: Correct the data in this line, or adjust the amount format
          settings on the import Type, then retry the queue job"""
                )
                % (
                    self.import_id.name or str(self.import_id.id),
                    self.sequence,
                    value,
                    ctype.amount_format,
                    ctype.amount_thousand_separator,
                    ctype.amount_decimal_separator,
                )
            ) from error

    def _parse_date(self, value, date_format):
        """Parse ``value`` into a date using ``date_format``. Raise UserError
        if it cannot be parsed."""
        self.ensure_one()
        try:
            return datetime.strptime(
                str(value).strip(), (date_format or "%Y-%m-%d").strip()
            ).date()
        except (ValueError, TypeError) as error:
            raise UserError(
                _(
                    """
Context: Processing customer payment import data line
Document: %s (sequence %s)
Problem: Could not parse date value '%s' using format '%s'
Solution: Verify the Date Format on the import Type matches the actual data,
          correct the data in this line, then retry the queue job"""
                )
                % (
                    self.import_id.name or str(self.import_id.id),
                    self.sequence,
                    value,
                    date_format,
                )
            ) from error

    def _find_existing_payment_by_unique_ref(self, unique_ref):
        """Return the account.payment already created for another data line
        sharing the same unique reference (same import Type), or an empty
        recordset. Used to avoid duplicate payments across separate imports."""
        self.ensure_one()
        if not unique_ref:
            return self.env["account.payment"]
        candidates = self.search(
            [
                ("id", "!=", self.id),
                ("payment_id", "!=", False),
                ("import_id.type_id", "=", self._get_type().id),
            ]
        )
        for candidate in candidates:
            ctype = candidate._get_type()
            if not ctype.unique_ref_column:
                continue
            candidate_ref = candidate._get_row_data().get(ctype.unique_ref_column)
            if str(candidate_ref or "").strip() == str(unique_ref).strip():
                return candidate.payment_id
        return self.env["account.payment"]

    # -------------------------------------------------------------------
    # Queue job methods
    # -------------------------------------------------------------------

    def _process_payment(self):
        """Entry point called by the queue job.

        Runs the actual conversion inside a savepoint so that any
        partially created payment is rolled back on failure -- the
        savepoint releases the row locks taken by
        ``_run_process_payment`` before the failure is recorded.
        Unlike a savepoint-only rollback, failures now **raise out of
        the job**: the error is recorded on the line through
        ``_write_error_result`` (a separate cursor, since this job's
        whole transaction is about to be rolled back once the
        exception propagates), then the original exception is
        re-raised so ``queue_job`` marks the job ``failed`` with
        ``exc_info`` instead of ``done``. This keeps
        ``queue.job.batch`` from reporting ``finished`` while a line
        is still unresolved, so the parent import is not moved to
        ``done`` prematurely. When ``_run_process_payment`` reports
        that the line already resolved itself (currently: excluded
        rows, written to ``state='ignored'``), the final
        unconditional ``state='done'`` write below is skipped,
        otherwise it would overwrite the ``ignored`` state. On both
        success paths, ``import_id._try_action_done()`` is called as
        the last step so the parent import is re-evaluated for
        completion right when this line settles -- regardless of
        whether the job that resolved it belongs to a
        ``queue.job.batch`` or was requeued outside of one by
        ``_retry()``. The failure path re-raises instead, so an
        unresolved line never triggers this re-evaluation.

        :return: ``True``
        :raises Exception: re-raises whatever
            ``_run_process_payment`` raised, after recording it on
            this line, so the queue job ends up ``failed``
        """
        self.ensure_one()
        if self.state in ("done", "ignored"):
            return True
        try:
            with self.env.cr.savepoint():
                already_resolved = self._run_process_payment()
        except Exception as error:  # pylint: disable=broad-except
            self._write_error_result(str(error))
            raise
        if already_resolved:
            self.import_id._try_action_done()
            return True
        self.write({"state": "done", "error_message": False})
        self.import_id._try_action_done()
        return True

    def _write_error_result(self, message):
        """Record a processing failure so it survives the rollback.

        Writes ``state='error'`` and ``error_message=message``
        through a brand-new cursor obtained from the registry, and
        commits it immediately -- by the time this is called from
        ``_process_payment``, the caller's own transaction is about
        to be rolled back entirely once the triggering exception
        propagates, so writing through ``self.env.cr`` would be lost.

        Flushes ``self.env`` first, through the still-valid running
        cursor. Odoo's pending-recompute queue is shared by every
        environment in the current thread, regardless of which
        cursor created them, so leaving it unflushed would make the
        new cursor's commit below try to recompute records that only
        exist in this (uncommitted) transaction, using a connection
        that cannot see them.

        Fallback: when this record is not yet visible to the new
        cursor (``exists()`` empty -- e.g. the record was created
        earlier in the same, not-yet-committed transaction, as
        happens in unit tests), write through the running cursor
        instead.

        :param message: error message to store on ``error_message``
        :return: ``True``
        """
        self.ensure_one()
        self.env["base"].flush()
        with registry(self.env.cr.dbname).cursor() as new_cr:
            new_env = api.Environment(new_cr, self.env.uid, self.env.context)
            record = new_env[self._name].browse(self.id)
            if record.exists():
                record.write({"state": "error", "error_message": message})
                return True
        self.write({"state": "error", "error_message": message})
        return True

    def _check_exclude(self, row):
        """Check whether ``row`` must be discarded before processing.

        Based on the import Type's Exclude Column / Exclude Values.
        When it matches, this line is written directly to
        ``state='ignored'`` with an auto-filled ``ignore_reason``, and
        ``payment_id`` is never touched.

        :param row: dict of column name/index to cell value, as
            returned by ``_get_row_data``
        :return: ``True`` when the row was excluded, ``False``
            otherwise
        """
        self.ensure_one()
        ctype = self._get_type()
        exclude_tokens = ctype._get_exclude_value_tokens()
        if not exclude_tokens:
            return False
        value = str(row.get(ctype.exclude_column, "") or "").strip()
        if value not in exclude_tokens:
            return False
        self.write(
            {
                "state": "ignored",
                "ignore_reason": _(
                    "Row excluded before processing: column '%s' has value "
                    "'%s', which matches the Exclude Values configured on "
                    "the import Type."
                )
                % (ctype.exclude_column, value),
            }
        )
        return True

    def _run_process_payment(self):  # pylint: disable=too-many-locals
        """Parse the raw JSON data line and create an account.payment
        according to the import Type's column mapping. Idempotent: if
        payment_id is already set, does nothing, so a retry never
        creates a duplicate payment.

        :return: ``True`` when the line already resolved itself
            (currently: excluded rows written to ``state='ignored'``),
            meaning the caller must not overwrite it with
            ``state='done'``; a falsy value for the normal
            create-payment path
        """
        self.ensure_one()
        if self.payment_id:
            return False

        ctype = self._get_type()
        row = self._get_row_data()
        imp = self.import_id

        if self._check_exclude(row):
            return True

        acc_number = row.get(ctype.partner_bank_account_column)
        partner = self._find_partner_by_bank_account(acc_number)
        if not partner:
            raise UserError(
                _(
                    """
Context: Processing customer payment import data line
Document: %s (sequence %s)
Problem: No partner found with bank account number '%s'
Solution: Register the bank account on the partner (res.partner.bank),
          correct the data in this line, then retry the queue job"""
                )
                % (imp.name or str(imp.id), self.sequence, acc_number)
            )

        unique_ref = (
            row.get(ctype.unique_ref_column) if ctype.unique_ref_column else False
        )
        existing_payment = self._find_existing_payment_by_unique_ref(unique_ref)
        if existing_payment:
            self.payment_id = existing_payment.id
            return

        amount = self._parse_amount(row.get(ctype.amount_column))
        payment_date = self._parse_date(row.get(ctype.date_column), ctype.date_format)
        communication = (
            row.get(ctype.communication_column) if ctype.communication_column else False
        )

        payment = self.env["account.payment"].create(
            self._prepare_payment_data(partner, amount, payment_date, communication)
        )
        if ctype.auto_post:
            payment.action_post()
        self.payment_id = payment.id

    def _get_destination_account(self, row, partner):
        """Resolve the destination account of this line's payment.

        Walks an ordered fallback chain and returns the first
        non-empty result; an unmapped usage is never an error:

        1. the account mapped to the row's usage on the import Type,
           when the Type has a ``usage_column`` configured and the
           row's value matches one of its mapping lines;
        2. the ``account_id`` of the import document header;
        3. the paying partner's default receivable account.

        Extension point: override to add another source, or to reorder
        the chain, without touching ``_prepare_payment_data``.

        :param row: dict of column name/index to cell value, as
            returned by ``_get_row_data``
        :param partner: ``res.partner`` record being paid
        :return: an ``account.account`` recordset, empty when every
            step of the chain came back empty
        """
        self.ensure_one()
        ctype = self._get_type()
        if ctype.usage_column:
            account = ctype._get_account_by_usage(row.get(ctype.usage_column))
            if account:
                return account
        if self.import_id.account_id:
            return self.import_id.account_id
        return partner.property_account_receivable_id

    def _prepare_payment_data(self, partner, amount, payment_date, communication):
        """Build the ``create`` vals for the resulting ``account.payment``.

        The destination account comes from ``_get_destination_account``
        and is only written when that resolution returned something, so
        that a document without any account configured keeps letting
        ``account.payment`` compute its own default.

        :param partner: ``res.partner`` record to pay
        :param amount: payment amount
        :param payment_date: payment date
        :param communication: payment reference/communication, or
            ``False``
        :return: dict of vals for ``account.payment``
        """
        self.ensure_one()
        imp = self.import_id
        vals = {
            "payment_type": "inbound",
            "partner_type": "customer",
            "partner_id": partner.id,
            "journal_id": imp.journal_id.id,
            "amount": amount,
            "date": payment_date,
            "ref": communication,
        }
        account = self._get_destination_account(self._get_row_data(), partner)
        if account:
            vals["destination_account_id"] = account.id
        return vals

    def _cancel_payment(self):
        """Cancel (if posted) or delete (if still draft) the linked
        account.payment, and clear the link."""
        self.ensure_one()
        if not self.payment_id:
            return

        payment = self.payment_id
        self.payment_id = False
        if payment.state == "posted":
            payment.action_cancel()
        elif payment.state == "draft":
            payment.unlink()

    # -------------------------------------------------------------------
    # Action methods
    # -------------------------------------------------------------------

    def action_ignore(self):
        """Ignore the selected data lines.

        Delegates to ``_ignore`` under ``sudo``.
        """
        for record in self.sudo():
            record._ignore()

    def action_retry(self):
        """Retry processing the selected data lines.

        Delegates to ``_retry`` under ``sudo``.
        """
        for record in self.sudo():
            record._retry()

    def action_open_ignore_wizard(self):
        """Open the wizard used to fill in the ignore reason.

        Delegates to ``_open_ignore_wizard`` under ``sudo``.

        :return: an ``ir.actions.act_window`` dict
        """
        for record in self.sudo():
            result = record._open_ignore_wizard()
        return result

    def action_open_edit_data_wizard(self):
        """Open the wizard used to edit this line's raw JSON data.

        Delegates to ``_open_edit_data_wizard`` under ``sudo``.

        :return: an ``ir.actions.act_window`` dict
        """
        for record in self.sudo():
            result = record._open_edit_data_wizard()
        return result

    def _open_ignore_wizard(self):
        """Build the window action for the ignore-reason wizard.

        :return: a copy of the ignore wizard action, with
            ``default_data_id`` set in its context to this record
        """
        self.ensure_one()
        waction = self.env.ref(
            "ssi_customer_payment_import.ignore_customer_payment_import_data_action"
        ).read()[0]
        waction.update({"context": {"default_data_id": self.id}})
        return waction

    def _open_edit_data_wizard(self):
        """Build the window action for the edit-data wizard.

        :return: a copy of the edit-data wizard action, with
            ``default_data_id`` set in its context to this record
        """
        self.ensure_one()
        waction = self.env.ref(
            "ssi_customer_payment_import.edit_customer_payment_import_data_action"
        ).read()[0]
        waction.update({"context": {"default_data_id": self.id}})
        return waction

    def _ignore(self):
        """Move the line to ``ignored`` after validating its state.

        Raises ``UserError`` when the line is not in ``draft``/
        ``error`` state, or when ``ignore_reason`` is empty. Also
        forces the linked queue job to ``done`` and re-evaluates the
        parent import's completion.
        """
        self.ensure_one()
        if self.state not in ("draft", "error"):
            raise UserError(
                _(
                    """
Context: Ignoring customer payment import data line
Document: %s (sequence %s)
Problem: This line is in state '%s' and cannot be ignored
Solution: Only lines in Draft or Error state can be ignored"""
                )
                % (
                    self.import_id.name or str(self.import_id.id),
                    self.sequence,
                    self.state,
                )
            )
        if not self.ignore_reason:
            raise UserError(
                _(
                    """
Context: Ignoring customer payment import data line
Document: %s (sequence %s)
Problem: Ignore reason is empty
Solution: Fill in the ignore reason before ignoring this line"""
                )
                % (self.import_id.name or str(self.import_id.id), self.sequence)
            )
        self.write({"state": "ignored"})
        self._force_queue_job_done()
        self.import_id._try_action_done()

    def _retry(self):
        """Reset the line to ``draft`` and requeue it for processing.

        Raises ``UserError`` unless the line is currently ``draft``
        or ``error`` -- retrying a ``done``/``ignored`` line would
        silently reprocess an already-settled row. Clears
        ``error_message``, then requeues through the job queue
        instead of calling ``_process_payment`` synchronously: when
        ``queue_job_id`` is set, ``queue_job_id.requeue()`` puts that
        job back to ``pending`` so the job runner executes it again;
        when it is empty (rows created before this field was
        tracked), a brand-new job is enqueued the same way
        ``_01_create_payment_on_queue_done`` does, and its record is
        stored back on ``queue_job_id``. Finally re-evaluates the
        parent import's completion.
        """
        self.ensure_one()
        if self.state not in ("draft", "error"):
            raise UserError(
                _(
                    """
Context: Retrying customer payment import data line
Document: %s (sequence %s)
Problem: This line is in state '%s' and cannot be retried
Solution: Only lines in Draft or Error state can be retried"""
                )
                % (
                    self.import_id.name or str(self.import_id.id),
                    self.sequence,
                    self.state,
                )
            )
        self.write({"state": "draft", "error_message": False})
        if self.queue_job_id:
            self.queue_job_id.requeue()
        else:
            description = "Create customer payment for data line ID %s" % self.id
            job = (
                self.with_context(job_batch=self.import_id.done_queue_job_batch_id)
                .with_delay(description=_(description))
                ._process_payment()
            )
            self.queue_job_id = job.db_record().id
        self.import_id._try_action_done()

    def _force_queue_job_done(self):
        """Force this line's queue job to ``done`` if not already.

        When ``queue_job_id`` is empty -- rows created before that
        field was tracked, or rows where writing it back once failed
        -- the matching job is looked up in the parent import's
        ``done_queue_job_ids`` by comparing ``model_name`` to this
        model and checking whether this record's id is in the job's
        ``records`` recordset. ``records`` is a ``JobSerialized``
        field, so it cannot be used inside a ``search()`` domain; the
        comparison is done in Python over the batch's job recordset
        instead. A job found this way is written back to
        ``queue_job_id`` before being forced to ``done``, so this
        lookup only has to happen once per line. When no matching job
        exists -- e.g. the import never reached ``queue_done`` for
        this line -- nothing is done and no error is raised, since
        that is not an error condition.

        :return: ``True``
        """
        self.ensure_one()
        if not self.queue_job_id:
            job = self.import_id.done_queue_job_ids.filtered(
                lambda job: job.model_name == self._name and self.id in job.records.ids
            )
            if job:
                self.queue_job_id = job[0].id
        if self.queue_job_id:
            if self.queue_job_id.state != "done":
                self.queue_job_id.button_done()
        return True
