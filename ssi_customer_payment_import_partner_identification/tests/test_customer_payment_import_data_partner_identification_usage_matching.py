# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.exceptions import UserError
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

    def test_process_payment_identification_ambiguous_usage_leaves_line_in_error(
        self,
    ):
        """``_process_payment`` on an identification-matched partner
        with ambiguous usage writes ``error``.

        Pure Python -- trigger P13 (L-26: YAML's ``expect_error`` runs
        the call inside a savepoint that gets rolled back once the
        expected exception is caught, so the ``_write_error_result``
        write ``_process_payment`` performs in its ``except`` block
        before re-raising would be lost if asserted via YAML). The
        YAML scenario "Identification partner match combined with
        partner_bank usage raises when the matched partner's eligible
        bank accounts carry more than one usage" already proves the
        ``UserError`` is raised with the right message; calling
        ``_process_payment`` directly here, with no savepoint around
        it, keeps the ``state='error'`` write visible for assertion.
        Unlike ``test_process_payment_ambiguous_usage_leaves_line_in_error``
        in ``ssi_customer_payment_import``, the partner here is
        resolved from ``res.partner.id_number`` (identification axis)
        rather than from the row's account number -- the axis this
        module adds.
        """
        bank = self.env["res.bank"].create(
            {"name": "Test Bank Identification Ambiguous Usage P13"}
        )
        journal_bank_account = self.env["res.partner.bank"].create(
            {
                "acc_number": "8500000099",
                "bank_id": bank.id,
                "partner_id": self.env.company.partner_id.id,
            }
        )
        journal = self.env["account.journal"].create(
            {
                "name": "Test Journal Identification Ambiguous Usage P13",
                "type": "bank",
                "bank_account_id": journal_bank_account.id,
            }
        )
        category = self.env["res.partner.id_category"].create(
            {
                "code": "PYTTIDU13",
                "name": "Identification Ambiguous Usage P13 Category",
            }
        )
        partner = self.env["res.partner"].create(
            {
                "name": "Identification Ambiguous Usage P13 Partner",
                "is_company": True,
            }
        )
        self.env["res.partner.id_number"].create(
            {
                "name": "PK-P13-1",
                "category_id": category.id,
                "partner_id": partner.id,
            }
        )
        usage_a = self.env["res_partner_bank_usage"].create(
            {
                "name": "Uang Sekolah - Identification Ambiguous Usage P13",
                "code": "PYTTIDUA13",
            }
        )
        usage_b = self.env["res_partner_bank_usage"].create(
            {
                "name": "Uang Pangkal - Identification Ambiguous Usage P13",
                "code": "PYTTIDUB13",
            }
        )
        account_a = self.env["account.account"].create(
            {
                "name": "Piutang A - Identification Ambiguous Usage P13",
                "code": "PYTTIDACA13",
                "user_type_id": self.env.ref("account.data_account_type_receivable").id,
                "reconcile": True,
            }
        )
        account_b = self.env["account.account"].create(
            {
                "name": "Piutang B - Identification Ambiguous Usage P13",
                "code": "PYTTIDACB13",
                "user_type_id": self.env.ref("account.data_account_type_receivable").id,
                "reconcile": True,
            }
        )
        self.env["res.partner.bank"].create(
            {
                "acc_number": "8500000096",
                "bank_id": bank.id,
                "partner_id": partner.id,
                "usage_id": usage_a.id,
            }
        )
        self.env["res.partner.bank"].create(
            {
                "acc_number": "8500000097",
                "bank_id": bank.id,
                "partner_id": partner.id,
                "usage_id": usage_b.id,
            }
        )
        ctype = self.env["customer_payment_import_type"].create(
            {
                "name": "Identification Ambiguous Usage P13 Test Type",
                "code": "PYTTIDT13",
                "date_column": "date",
                "amount_column": "amount",
                "partner_matching_method": "identification",
                "partner_identification_column": "id_no",
                "partner_id_category_id": category.id,
                "usage_matching_method": "partner_bank",
                "account_mapping_ids": [
                    (
                        0,
                        0,
                        {
                            "sequence": 10,
                            "usage_id": usage_a.id,
                            "account_id": account_a.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "sequence": 20,
                            "usage_id": usage_b.id,
                            "account_id": account_b.id,
                        },
                    ),
                ],
            }
        )
        import_doc = self.env["customer_payment_import"].create(
            {"type_id": ctype.id, "journal_id": journal.id}
        )
        data_line = self.env["customer_payment_import.data"].create(
            {
                "import_id": import_doc.id,
                "sequence": 1,
                "data": '{"date": "2026-04-01", '
                '"id_no": "PK-P13-1", "amount": "60000"}',
            }
        )

        with self.assertRaises(UserError):
            data_line._process_payment()

        self.assertEqual(data_line.state, "error")
