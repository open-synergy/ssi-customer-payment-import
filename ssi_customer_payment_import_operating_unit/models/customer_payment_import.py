# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import UserError


class CustomerPaymentImport(models.Model):
    """Add Operating Unit awareness to ``customer_payment_import``.

    ``operating_unit_id`` comes from ``mixin.single_operating_unit``,
    defaulted from the creating user's Operating Unit. Consistency with
    ``journal_id`` is kept via the ``allowed_journal_ids`` filter, an
    onchange that clears the journal, and a data-level constraint
    against ``journal_id.operating_unit_ids`` (``mixin.multiple_
    operating_unit``, added to ``account.journal`` by the glue module
    ``ssi_financial_accounting_operating_unit``). This replicates the
    pattern used there for ``account.move`` (``models/account_move.py``),
    minus its replacement-journal self-heal — here the journal is only
    cleared, and the user re-selects manually. The resulting
    ``account.payment`` is out of scope for this module; only
    ``journal_id`` selection on the import document itself is guarded.
    """

    _name = "customer_payment_import"
    _inherit = [
        "customer_payment_import",
        "mixin.single_operating_unit",
    ]

    @api.depends("type_id", "operating_unit_id")
    def _compute_allowed_journal_ids(self):
        """Filter ``allowed_journal_ids`` by Operating Unit.

        Runs the base M2O configurator filter first (``type_id``), then
        for records with an ``operating_unit_id`` narrows the result to
        journals whose ``operating_unit_ids`` either is empty (cross-OU
        journal, always allowed) or contains the document's
        ``operating_unit_id``. Records without an ``operating_unit_id``
        keep the base result unfiltered.
        """
        super()._compute_allowed_journal_ids()
        for record in self:
            if record.operating_unit_id:
                journals = record.allowed_journal_ids
                record.allowed_journal_ids = journals.filtered(
                    lambda j: not j.operating_unit_ids
                    or record.operating_unit_id in j.operating_unit_ids
                )

    @api.onchange("operating_unit_id")
    def _onchange_operating_unit(self):
        """Clear ``journal_id`` when it no longer matches the new OU.

        If the currently selected ``journal_id`` has
        ``operating_unit_ids`` set and it does not contain the new
        ``operating_unit_id``, ``journal_id`` is emptied so the user picks
        a compatible one. Journals without ``operating_unit_ids``
        (cross-OU) are never cleared by this onchange.
        """
        if (
            self.journal_id
            and self.journal_id.operating_unit_ids
            and self.operating_unit_id not in self.journal_id.operating_unit_ids
        ):
            self.journal_id = False

    @api.constrains("operating_unit_id", "journal_id")
    def _check_journal_operating_unit(self):
        """Validate ``journal_id`` matches ``operating_unit_id``.

        Data-level gate complementing the ``allowed_journal_ids`` filter
        and the onchange above, which only apply to the form UI and do
        not stop ``create()``/``write()`` reached through other paths
        (import, server action, other module code). Raises ``UserError``
        when ``journal_id.operating_unit_ids`` is set and does not
        contain ``operating_unit_id``. Either being empty passes.
        """
        for record in self:
            if (
                record.journal_id.operating_unit_ids
                and record.operating_unit_id
                and record.operating_unit_id.id
                not in record.journal_id.operating_unit_ids.ids
            ):
                error_message = _(
                    """
Context: Confirm Customer Payment Import
Database ID: %s
Problem: Operating Unit %s does not match Journal %s's Operating Unit(s)
Solution: Set the same Operating Unit as the Journal, or select another \
Journal
"""
                    % (
                        record.id,
                        record.operating_unit_id.name,
                        record.journal_id.name,
                    )
                )
                raise UserError(error_message)
