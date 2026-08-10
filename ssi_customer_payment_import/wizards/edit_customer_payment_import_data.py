# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class EditCustomerPaymentImportData(models.TransientModel):
    """
    Wizard to correct the raw JSON data of a single customer payment
    import data line, opened from the "Edit Data" button on the import
    data line. Confirming sends the line back to draft so the user can
    retry it manually.
    """

    _name = "edit_customer_payment_import_data"
    _description = "Customer Payment Import Data - Edit Raw Data"

    @api.model
    def _default_data_id(self):
        """Default ``data_id`` to the record the wizard was opened from.

        :return: ``active_id`` from the context, or ``False``
        """
        return self.env.context.get("active_id", False)

    @api.model
    def _default_data(self):
        """Default ``data`` to the current raw JSON of ``data_id``.

        :return: the data line's ``data`` value, or ``False`` when
            ``_default_data_id`` resolves to nothing
        """
        data_id = self._default_data_id()
        if not data_id:
            return False
        return self.env["customer_payment_import.data"].browse(data_id).data

    data_id = fields.Many2one(
        string="Data Line",
        comodel_name="customer_payment_import.data",
        required=True,
        default=lambda self: self._default_data_id(),
        help="The import data line whose raw data will be corrected.",
    )
    data = fields.Text(
        string="Data",
        required=True,
        default=lambda self: self._default_data(),
        help="Raw row data to replace the current data line content with, "
        "as a JSON object.",
    )

    def action_confirm(self):
        """Apply the corrected raw data.

        Delegates to ``_confirm`` under ``sudo``.
        """
        for record in self.sudo():
            record._confirm()

    def _confirm(self):
        """Validate and write the corrected raw data to ``data_id``.

        Raises ``UserError`` when ``data_id`` is not in ``draft``/
        ``error`` state, or when ``data`` is not a valid JSON object.
        On success, writes the new ``data``, resets ``state`` to
        ``draft`` and clears ``error_message``.
        """
        self.ensure_one()
        if self.data_id.state not in ("draft", "error"):
            raise UserError(
                _(
                    """
Context: Editing customer payment import data line raw data
Document: %s (sequence %s)
Problem: This line is in state '%s' and cannot have its raw data edited
Solution: Only lines in Draft or Error state can be edited"""
                )
                % (
                    self.data_id.import_id.name or str(self.data_id.import_id.id),
                    self.data_id.sequence,
                    self.data_id.state,
                )
            )
        try:
            parsed = json.loads(self.data)
        except (ValueError, TypeError):
            parsed = None
        if not isinstance(parsed, dict):
            raise UserError(
                _(
                    """
Context: Editing customer payment import data line raw data
Document: %s (sequence %s)
Problem: Data is not a valid JSON object
Solution: Correct the data so that it is a valid JSON object, then confirm again"""
                )
                % (
                    self.data_id.import_id.name or str(self.data_id.import_id.id),
                    self.data_id.sequence,
                )
            )
        self.data_id.write(
            {
                "data": json.dumps(parsed),
                "state": "draft",
                "error_message": False,
            }
        )
