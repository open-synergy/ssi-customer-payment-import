# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class CustomerPaymentImportData(models.Model):  # pylint: disable=too-few-public-methods
    """Add Partner Identification matching to
    ``customer_payment_import.data``.

    Overrides ``_find_partner`` to dispatch to
    ``_find_partner_by_identification`` when the import Type's
    ``partner_matching_method`` is ``identification``, falling
    through to ``super()._find_partner(row)`` for every other value --
    the same extension pattern already used for ``bank`` matching.
    """

    _name = "customer_payment_import.data"
    _inherit = ["customer_payment_import.data"]

    def _find_partner(self, row):
        """Resolve the paying res.partner for ``row``.

        Extension point override: adds the ``identification`` branch
        to the ``partner_matching_method`` dispatch, then falls
        through to ``super()._find_partner(row)`` for every other
        value.

        :param row: dict of column name/index to cell value, as
            returned by ``_get_row_data``
        :return: matched ``res.partner`` recordset
        :raises odoo.exceptions.UserError: propagated from
            ``_find_partner_by_identification`` when the identification
            matching method resolves to zero or more than one partner
        """
        self.ensure_one()
        ctype = self._get_type()
        if ctype.partner_matching_method == "identification":
            return self._find_partner_by_identification(row)
        return super()._find_partner(row)

    def _find_partner_by_identification(self, row):
        """Return the res.partner whose res.partner.id_number matches
        the identification value read from ``row``.

        The value is read from ``partner_identification_column`` and
        only stripped -- unlike ``_find_partner_by_bank_account`` it
        is never passed through ``sanitize_account_number``, since an
        identification value such as ``"PK-1786164942"`` would lose
        its ``-`` and be upper-cased by that helper, corrupting the
        comparison. The search domain always includes
        ``partner_id_category_id``, so an identical value registered
        under a different category never matches; the search runs
        without ``limit=1`` -- unlike ``res.partner.bank``,
        ``res.partner.id_number`` has no unique constraint, so more
        than one match is a real, ambiguous outcome that must be
        raised instead of silently picked.

        :param row: dict of column name/index to cell value, as
            returned by ``_get_row_data``
        :return: matched ``res.partner`` recordset
        :raises odoo.exceptions.UserError: no ``res.partner.id_number``
            matches the value under the configured category, or more
            than one does
        """
        self.ensure_one()
        ctype = self._get_type()
        category = ctype.partner_id_category_id
        value = str(row.get(ctype.partner_identification_column) or "").strip()
        id_numbers = self.env["res.partner.id_number"].search(
            [
                ("category_id", "=", category.id),
                ("name", "=", value),
            ]
        )
        imp = self.import_id
        if not id_numbers:
            raise UserError(
                _(
                    """
Context: Processing customer payment import data line
Document: %s (sequence %s)
Problem: No partner found with identification value '%s' under
         category '%s'
Solution: Register the identification number on the partner
          (res.partner.id_number), correct the data in this line, or
          adjust Partner Identification Category on the import Type,
          then retry the queue job"""
                )
                % (
                    imp.name or str(imp.id),
                    self.sequence,
                    value,
                    category.display_name,
                )
            )
        if len(id_numbers) > 1:
            raise UserError(
                _(
                    """
Context: Processing customer payment import data line
Document: %s (sequence %s)
Problem: %s partners found with identification value '%s' under
         category '%s'
Solution: Ensure only one partner is registered with that
          identification value under this category
          (res.partner.id_number), correct the data in this line,
          then retry the queue job"""
                )
                % (
                    imp.name or str(imp.id),
                    self.sequence,
                    len(id_numbers),
                    value,
                    category.display_name,
                )
            )
        return id_numbers.partner_id
