# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import io

import openpyxl
from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestCustomerPaymentImport(YamlTransactionCase):
    """Cover the ``customer_payment_import`` document and its lines."""

    def test_customer_payment_import(self):
        """Run the ``customer_payment_import`` YAML scenario."""
        self.run_yaml_scenario("test_data_customer_payment_import.yaml")

    # -------------------------------------------------------------------
    # Cases not expressible in YAML (building binary XLSX content with
    # openpyxl needs real loops/objects, and the return value of the
    # wizard-opener actions is discarded by YAML's `call` action).
    # -------------------------------------------------------------------

    def _create_type(self, code, **extra_values):
        """Create a ``customer_payment_import_type`` with base columns.

        :param code: unique ``code`` value for the type
        :param extra_values: additional vals overriding/extending the
            base column mapping
        :return: ``customer_payment_import_type`` record
        """
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
        """Create a bank ``account.journal`` with the given name.

        :param name: journal name
        :return: ``account.journal`` record
        """
        return self.env["account.journal"].create({"name": name, "type": "bank"})

    def test_load_data_xlsx(self):
        """``action_load_data`` reads rows from an XLSX import file.

        Pure Python -- trigger P10 (L-09, L-10, L-11: the fixture
        builds a real binary ``.xlsx`` file with ``openpyxl`` and
        base64-encodes it, which the YAML ``EVAL:`` whitelist cannot
        express -- no loops, no ``import``, so ``openpyxl`` is out of
        reach).
        """
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

    def test_action_open_ignore_wizard_returns_scoped_action_window(self):
        """``action_open_ignore_wizard`` returns a scoped act_window dict.

        Pure Python -- trigger P1 (L-01, L-02: ``action: call`` YAML
        discards the method's return value, and every YAML assert
        target is a dotted ``getattr`` on a registry record, so the
        ``ir.actions.act_window`` dict itself cannot be inspected from
        YAML).

        Builds a data line directly in ``error`` state, without
        running ``action_load_data``, then asserts the wizard action
        points at the ignore-reason wizard model, opens as a dialog,
        and is pre-scoped to this data line via
        ``context["default_data_id"]``.
        """
        ctype = self._create_type(code="PYTT-IGW")
        journal = self._create_bank_journal("Test Journal Ignore Wizard")
        import_doc = self.env["customer_payment_import"].create(
            {"type_id": ctype.id, "journal_id": journal.id}
        )
        data_line = self.env["customer_payment_import.data"].create(
            {
                "import_id": import_doc.id,
                "sequence": 1,
                "state": "error",
                "error_message": "Sample error for ignore wizard action test",
            }
        )

        action = data_line.action_open_ignore_wizard()

        self.assertEqual(action["res_model"], "ignore_customer_payment_import_data")
        self.assertEqual(action["target"], "new")
        self.assertEqual(action["context"]["default_data_id"], data_line.id)

    def test_action_open_edit_data_wizard_returns_scoped_action_window(self):
        """``action_open_edit_data_wizard`` returns a scoped act_window.

        Pure Python -- trigger P1 (L-01, L-02: ``action: call`` YAML
        discards the method's return value, and every YAML assert
        target is a dotted ``getattr`` on a registry record, so the
        ``ir.actions.act_window`` dict itself cannot be inspected from
        YAML).

        Builds a data line directly in ``error`` state, without
        running ``action_load_data``, then asserts the wizard action
        points at the edit-data wizard model, opens as a dialog, and
        is pre-scoped to this data line via
        ``context["default_data_id"]``.
        """
        ctype = self._create_type(code="PYTT-EDW")
        journal = self._create_bank_journal("Test Journal Edit Data Wizard")
        import_doc = self.env["customer_payment_import"].create(
            {"type_id": ctype.id, "journal_id": journal.id}
        )
        data_line = self.env["customer_payment_import.data"].create(
            {
                "import_id": import_doc.id,
                "sequence": 1,
                "state": "error",
                "error_message": "Sample error for edit data wizard action test",
                "data": '{"emp": "OLD"}',
            }
        )

        action = data_line.action_open_edit_data_wizard()

        self.assertEqual(action["res_model"], "edit_customer_payment_import_data")
        self.assertEqual(action["target"], "new")
        self.assertEqual(action["context"]["default_data_id"], data_line.id)

    def _create_failed_job_data_line(self, code):
        """Build a data line with a real, previously-``failed`` job.

        Pure Python -- trigger P1 (L-01: ``with_delay()._process_payment()``
        chains two method calls into one expression -- ``with_delay()``
        returns a delayable, and only then is ``_process_payment``
        called on it -- which YAML's ``call`` action cannot express,
        since it only supports a single ``target.method(*args,
        **kwargs)`` dispatch, not chaining).

        Enqueues the job without ``queue_job__no_delay``, so
        ``with_delay()`` genuinely stores a ``queue.job`` record
        (state ``pending``) instead of running the job body inline.
        The job is then flipped to ``failed`` directly -- ``state``
        is not one of ``queue.job``'s protected fields, so this does
        not need the ``EDIT_SENTINEL`` bypass -- to simulate a data
        line whose previous processing attempt failed.

        :param code: unique ``code`` value for the fixture type
        :return: tuple of (data line, its ``queue.job`` record)
        """
        ctype = self._create_type(code=code)
        journal = self._create_bank_journal("Test Journal %s" % code)
        import_doc = self.env["customer_payment_import"].create(
            {"type_id": ctype.id, "journal_id": journal.id}
        )
        data_line = self.env["customer_payment_import.data"].create(
            {"import_id": import_doc.id, "sequence": 1}
        )
        job = data_line.with_delay(description="Test job %s" % code)._process_payment()
        job_record = job.db_record()
        job_record.write({"state": "failed"})
        data_line.write(
            {
                "state": "error",
                "error_message": "Sample error before retry/ignore",
                "queue_job_id": job_record.id,
            }
        )
        return data_line, job_record

    def test_retry_requeues_existing_failed_job(self):
        """``action_retry`` requeues an existing ``failed`` job.

        Pure Python -- trigger P1 (L-01: fixture needs
        ``with_delay()._process_payment()`` chaining, see
        ``_create_failed_job_data_line``).

        The job is put back to ``pending`` (so the job runner picks
        it up again) and the line is reset to ``draft`` with no
        error message, without ``_retry`` ever calling
        ``_process_payment`` synchronously.
        """
        data_line, job_record = self._create_failed_job_data_line("PYTT-RETRYQ")

        data_line.action_retry()

        self.assertEqual(job_record.state, "pending")
        self.assertEqual(data_line.state, "draft")
        self.assertFalse(data_line.error_message)

    def test_ignore_forces_existing_failed_job_done(self):
        """``action_ignore`` forces an existing ``failed`` job to ``done``.

        Pure Python -- trigger P1 (L-01: fixture needs
        ``with_delay()._process_payment()`` chaining, see
        ``_create_failed_job_data_line``).
        """
        data_line, job_record = self._create_failed_job_data_line("PYTT-IGNOREQ")
        data_line.ignore_reason = "Duplicate row, safe to ignore"

        data_line.action_ignore()

        self.assertEqual(data_line.state, "ignored")
        self.assertEqual(job_record.state, "done")
