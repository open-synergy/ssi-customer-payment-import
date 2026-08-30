# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestCustomerPaymentImportOperatingUnit(YamlTransactionCase):
    """Test Operating Unit behavior on ``customer_payment_import``.

    Covers ``operating_unit_id`` propagation/defaulting, the
    ``allowed_journal_ids`` Operating Unit filter on both saved
    records and unsaved (``NewId``) Form records, the onchange that
    clears a mismatched ``journal_id``, the
    ``_check_journal_operating_unit`` data-level constraint, and (in
    ``test_customer_payment_import_operating_unit_payment``) the
    propagation of that Operating Unit onto the ``account.payment``
    created from a data line.
    """

    def test_customer_payment_import_operating_unit(self):
        """Run all Operating Unit scenarios for ``customer_payment_import``."""
        self.run_yaml_scenario("test_data_customer_payment_import_operating_unit.yaml")

    def test_customer_payment_import_operating_unit_payment(self):
        """Run the ``account.payment`` Operating Unit propagation scenarios.

        Separate YAML file (T-01): these scenarios create their own
        ``customer_payment_import_type``/``account.journal`` fixtures
        and run the full confirm/approve workflow, which would collide
        with the ``setup:``-free fixtures replayed by the scenarios in
        ``test_data_customer_payment_import_operating_unit.yaml`` if
        sharing one file.
        """
        self.run_yaml_scenario(
            "test_data_customer_payment_import_operating_unit_payment.yaml"
        )
