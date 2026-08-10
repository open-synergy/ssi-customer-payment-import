# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestCustomerPaymentImportOperatingUnit(YamlTransactionCase):
    """Test Operating Unit behavior on ``customer_payment_import``.

    Covers ``operating_unit_id`` propagation/defaulting, the
    ``allowed_journal_ids`` Operating Unit filter, the onchange that
    clears a mismatched ``journal_id``, and the
    ``_check_journal_operating_unit`` data-level constraint.
    """

    def test_customer_payment_import_operating_unit(self):
        """Run all Operating Unit scenarios for ``customer_payment_import``."""
        self.run_yaml_scenario("test_data_customer_payment_import_operating_unit.yaml")
