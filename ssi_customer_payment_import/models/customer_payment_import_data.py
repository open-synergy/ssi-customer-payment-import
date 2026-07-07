# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from datetime import datetime

from odoo import _, fields, models
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
        self.ensure_one()
        if not self.data:
            return {}
        try:
            return json.loads(self.data)
        except (ValueError, TypeError):
            return {}

    def _get_type(self):
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
        separators) into a float. Raise UserError if it cannot be parsed."""
        self.ensure_one()
        if isinstance(value, (int, float)):
            return float(value)

        text = str(value or "").strip().replace(" ", "")
        if "," in text and "." in text:
            if text.rfind(",") > text.rfind("."):
                text = text.replace(".", "").replace(",", ".")
            else:
                text = text.replace(",", "")
        elif "," in text:
            text = text.replace(",", ".")

        try:
            return float(text)
        except ValueError as error:
            raise UserError(
                _(
                    """
Context: Processing customer payment import data line
Document: %s (sequence %s)
Problem: Could not parse amount value '%s'
Solution: Correct the data in this line, then retry the queue job"""
                )
                % (self.import_id.name or str(self.import_id.id), self.sequence, value)
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

    def _process_payment(self):  # pylint: disable=too-many-locals
        """Parse the raw JSON data line and create an account.payment
        according to the import Type's column mapping. Idempotent: if
        payment_id is already set, skip to prevent duplicates on retry."""
        self.ensure_one()
        if self.payment_id:
            return

        ctype = self._get_type()
        row = self._get_row_data()
        imp = self.import_id

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

    def _prepare_payment_data(self, partner, amount, payment_date, communication):
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
        if imp.account_id:
            vals["destination_account_id"] = imp.account_id.id
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
