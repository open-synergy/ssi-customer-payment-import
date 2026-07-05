# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import io

import openpyxl
from odoo_yaml_test import YamlTransactionCase

from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestCustomerPaymentImport(YamlTransactionCase):
    def test_customer_payment_import(self):
        self.run_yaml_scenario("test_data_customer_payment_import.yaml")

    # -------------------------------------------------------------------
    # Cases not expressible in YAML (the odoo-yaml-test framework has no
    # "expect this action to raise" step, and building binary XLSX content
    # is far cleaner in Python than embedding a large base64 blob in YAML).
    # -------------------------------------------------------------------

    def _create_type(self, code, **extra_values):
        values = {
            "name": "Python Test Type %s" % code,
            "code": code,
            "date_column": "date",
            "partner_bank_account_column": "account_number",
            "amount_column": "amount",
        }
        values.update(extra_values)
        return self.env["customer_payment_import_type"].create(values)

    def _create_bank_journal(self, name):
        return self.env["account.journal"].create({"name": name, "type": "bank"})

    def test_duplicate_import_file_hash_rejected(self):
        ctype = self._create_type(code="PYTT-DUP")
        journal = self._create_bank_journal("Test Journal Dup")
        content = base64.b64encode(b"date,account_number,amount\n2026-03-01,111,1000\n")

        doc1 = (
            self.env["customer_payment_import"]
            .with_user(self.env.ref("base.user_admin"))
            .create(
                {
                    "type_id": ctype.id,
                    "journal_id": journal.id,
                    "import_file": content,
                    "import_file_name": "dup.csv",
                }
            )
        )
        doc1.action_load_data()

        doc2 = (
            self.env["customer_payment_import"]
            .with_user(self.env.ref("base.user_admin"))
            .create(
                {
                    "type_id": ctype.id,
                    "journal_id": journal.id,
                    "import_file": content,
                    "import_file_name": "dup_2.csv",
                }
            )
        )
        with self.assertRaises(ValidationError):
            doc2.action_load_data()

    def test_process_payment_unknown_bank_account_raises_usererror(self):
        ctype = self._create_type(code="PYTT-UNK")
        journal = self._create_bank_journal("Test Journal Unknown")
        import_doc = self.env["customer_payment_import"].create(
            {"type_id": ctype.id, "journal_id": journal.id}
        )
        data_line = self.env["customer_payment_import.data"].create(
            {
                "import_id": import_doc.id,
                "sequence": 1,
                "data": (
                    '{"date": "2026-03-02", "account_number": '
                    '"0000000000", "amount": "1000"}'
                ),
            }
        )
        with self.assertRaises(UserError):
            data_line._process_payment()

    def test_process_payment_idempotent(self):
        ctype = self._create_type(code="PYTT-IDEM")
        journal = self._create_bank_journal("Test Journal Idem")
        partner = self.env["res.partner"].create(
            {"name": "Idempotent Partner", "is_company": True}
        )
        self.env["res.partner.bank"].create(
            {"acc_number": "7777777777", "partner_id": partner.id}
        )
        import_doc = self.env["customer_payment_import"].create(
            {"type_id": ctype.id, "journal_id": journal.id}
        )
        data_line = self.env["customer_payment_import.data"].create(
            {
                "import_id": import_doc.id,
                "sequence": 1,
                "data": (
                    '{"date": "2026-03-03", "account_number": '
                    '"7777777777", "amount": "50000"}'
                ),
            }
        )

        data_line._process_payment()
        first_payment_id = data_line.payment_id.id
        self.assertTrue(first_payment_id)

        data_line._process_payment()
        self.assertEqual(data_line.payment_id.id, first_payment_id)

        payment_count = self.env["account.payment"].search_count(
            [("partner_id", "=", partner.id), ("journal_id", "=", journal.id)]
        )
        self.assertEqual(payment_count, 1)

    def test_load_data_xlsx(self):
        ctype = self._create_type(
            code="PYTT-XLSX",
            file_type="xlsx",
            communication_column="description",
        )
        journal = self._create_bank_journal("Test Journal XLSX")

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(["date", "account_number", "amount", "description"])
        sheet.append(["2026-03-04", "8888888888", 200000, "XLSX Payment A"])
        sheet.append(["2026-03-05", "9999999999", 310000, "XLSX Payment B"])
        buffer = io.BytesIO()
        workbook.save(buffer)

        import_doc = self.env["customer_payment_import"].create(
            {
                "type_id": ctype.id,
                "journal_id": journal.id,
                "import_file": base64.b64encode(buffer.getvalue()),
                "import_file_name": "sample.xlsx",
            }
        )
        import_doc.action_load_data()

        self.assertEqual(len(import_doc.data_ids), 2)
        first_line = import_doc.data_ids.sorted("sequence")[0]
        row = first_line._get_row_data()
        self.assertEqual(row.get("account_number"), "8888888888")
        self.assertEqual(row.get("amount"), 200000)
        self.assertEqual(row.get("description"), "XLSX Payment A")
