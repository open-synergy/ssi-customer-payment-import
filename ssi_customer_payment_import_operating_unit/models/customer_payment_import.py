# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class CustomerPaymentImport(models.Model):
    _name = "customer_payment_import"
    _inherit = [
        "customer_payment_import",
        "mixin.single_operating_unit",
    ]
