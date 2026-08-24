# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CustomerPaymentImportType(models.Model):
    """Add Partner Identification matching to
    ``customer_payment_import_type``.

    Adds the ``identification`` choice to ``partner_matching_method``
    plus the two fields that configure it: the source column holding
    the identification value (``partner_identification_column``) and
    the ``res.partner.id_category`` it is matched against
    (``partner_id_category_id``). Both are required only when
    ``partner_matching_method`` is ``identification`` -- enforced by
    ``_check_partner_identification_matching_method`` below.
    """

    _name = "customer_payment_import_type"
    _inherit = ["customer_payment_import_type"]

    partner_matching_method = fields.Selection(
        selection_add=[("identification", "Partner Identification")],
        ondelete={"identification": "set default"},
    )
    partner_identification_column = fields.Char(
        string="Partner Identification Column",
        help=(
            "Column name (or 0-based index if No Header Line is checked) "
            "containing the identification number used to identify the "
            "paying customer, matched against res.partner.id_number. "
            "Required only when Partner Matching Method = Partner "
            "Identification."
        ),
    )
    partner_id_category_id = fields.Many2one(
        string="Partner Identification Category",
        comodel_name="res.partner.id_category",
        help=(
            "Identification category (res.partner.id_category) that "
            "Partner Identification Column values are matched against. "
            "Required only when Partner Matching Method = Partner "
            "Identification."
        ),
    )

    @api.constrains(
        "partner_matching_method",
        "partner_identification_column",
        "partner_id_category_id",
    )
    def _check_partner_identification_matching_method(self):
        """Reject an Identification matching method without its setup.

        Raises ``ValidationError`` when
        ``_check_partner_identification_matching_method_condition``
        fails.
        """
        for record in self:
            if not record._check_partner_identification_matching_method_condition():
                error_message = (
                    _(
                        """
Context: Saving customer payment import type
Type: %s
Problem: Partner Matching Method is 'Partner Identification' but
         Partner Identification Column or Partner Identification
         Category is empty
Solution: Fill in both Partner Identification Column and Partner
          Identification Category, or choose a different Partner
          Matching Method"""
                    )
                    % (record.display_name,)
                )
                raise ValidationError(error_message)

    def _check_partner_identification_matching_method_condition(self):
        """Return whether this Type's identification setup is
        complete.

        :return: ``False`` when ``partner_matching_method`` is
            ``"identification"`` and either
            ``partner_identification_column`` or
            ``partner_id_category_id`` is empty; ``True`` otherwise
        """
        self.ensure_one()
        if self.partner_matching_method != "identification":
            return True
        return bool(self.partner_identification_column and self.partner_id_category_id)
