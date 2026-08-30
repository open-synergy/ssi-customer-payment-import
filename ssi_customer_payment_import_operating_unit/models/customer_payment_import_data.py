# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class CustomerPaymentImportData(models.Model):  # pylint: disable=too-few-public-methods
    """Propagate the import document's Operating Unit to its payment.

    ``customer_payment_import`` (the header, see ``models/
    customer_payment_import.py``) carries ``operating_unit_id`` via
    ``mixin.single_operating_unit``, but the base module's
    ``_prepare_payment_data`` never forwards it to the ``account.payment``
    it creates. That leaves the resulting payment's journal entry
    (``account.payment.move_id``) to fall back to ``mixin.single_
    operating_unit``'s own default -- the Operating Unit of whichever
    user runs the import (often a queue job worker), not the document's.
    This class closes that gap by overriding ``_prepare_payment_data``.
    """

    _name = "customer_payment_import.data"
    _inherit = [
        "customer_payment_import.data",
    ]

    def _prepare_payment_data(self, partner, amount, payment_date, communication):
        """Add ``operating_unit_id`` to the ``account.payment`` create vals.

        Always takes ``import_id.operating_unit_id`` as-is, with no guard:
        the import document is the sole source of truth for the payment's
        Operating Unit, so a document left without one must produce a
        payment without one too, rather than silently inheriting whoever
        happens to run the queue job.

        :param partner: ``res.partner`` record to pay
        :param amount: payment amount
        :param payment_date: payment date
        :param communication: payment reference/communication, or
            ``False``
        :return: dict of vals for ``account.payment``, extended with
            ``operating_unit_id`` taken from the import document
        """
        self.ensure_one()
        res = super()._prepare_payment_data(
            partner, amount, payment_date, communication
        )
        res["operating_unit_id"] = self.import_id.operating_unit_id.id
        return res
