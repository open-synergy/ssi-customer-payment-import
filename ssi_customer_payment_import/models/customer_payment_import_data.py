# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo import fields, models


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
