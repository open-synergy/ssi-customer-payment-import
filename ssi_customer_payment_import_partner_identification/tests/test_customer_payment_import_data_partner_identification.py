# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestCustomerPaymentImportDataPartnerIdentification(YamlTransactionCase):
    """Cover ``_find_partner_by_identification`` on
    ``customer_payment_import.data``.
    """

    def test_customer_payment_import_data_partner_identification(self):
        """Run the Partner Identification matching YAML scenario."""
        self.run_yaml_scenario(
            "test_data_customer_payment_import_data_partner_identification.yaml"
        )
