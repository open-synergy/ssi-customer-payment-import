# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class IgnoreCustomerPaymentImportData(models.TransientModel):
    """
    Wizard to ignore a single customer payment import data line with a
    reason, opened from the "Ignore" button on the import data line.
    """

    _name = "ignore_customer_payment_import_data"
    _description = "Customer Payment Import Data - Ignore"

    @api.model
    def _default_data_id(self):
        """Default ``data_id`` to the record the wizard was opened from.

        :return: ``active_id`` from the context, or ``False``
        """
        return self.env.context.get("active_id", False)

    data_id = fields.Many2one(
        string="Data Line",
        comodel_name="customer_payment_import.data",
        required=True,
        default=lambda self: self._default_data_id(),
        help="The import data line that will be ignored.",
    )
    reason = fields.Text(
        string="Reason",
        required=True,
        help="Reason why this data line is ignored.",
    )

    def action_confirm(self):
        """Ignore the data line with the given reason.

        Delegates to ``_confirm`` under ``sudo``.
        """
        for record in self.sudo():
            record._confirm()

    def _confirm(self):
        """Write ``reason`` to ``data_id`` and ignore it.

        Sets ``ignore_reason`` then calls ``action_ignore`` on
        ``data_id``, which validates state and moves it to
        ``ignored``.
        """
        self.ensure_one()
        self.data_id.write({"ignore_reason": self.reason})
        self.data_id.action_ignore()
