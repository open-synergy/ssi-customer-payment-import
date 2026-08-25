# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestCustomerPaymentImportDataPartnerIdentificationUsageMatching(
    YamlTransactionCase
):
    """Cover the cross-axis combination of Partner Identification
    partner matching with independent usage matching.

    ``partner_matching_method`` and ``usage_matching_method`` are two
    separate configuration axes on ``customer_payment_import_type``
    since ``usage_matching_method`` was split out of
    ``partner_matching_method`` (open-synergy/ssi-customer-payment-
    import#42). This proves the combination that motivated the split:
    partner resolved from ``res.partner.id_number`` while the
    destination account is resolved from the bank account usage,
    either through the account number column or through the matched
    partner's own bank accounts.
    """

    def test_customer_payment_import_data_partner_identification_usage_matching(
        self,
    ):
        """Run the identification + usage matching YAML scenarios."""
        self.run_yaml_scenario(
            "test_data_customer_payment_import_data_partner_identification_usage_matching.yaml"  # noqa: E501
        )
