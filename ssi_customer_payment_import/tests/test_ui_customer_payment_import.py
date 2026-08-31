# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase -- NOT HttpCase. In 14.0, HttpCase does not set up
# cls.env in setUpClass, and every Pre-Condition here is prepared there.
from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiCustomerPaymentImport(HttpSavepointCase):
    """Tour tests for the ``customer_payment_import`` work instructions."""

    @classmethod
    def setUpClass(cls):
        """Create the master data and documents each tour needs.

        ``user_id`` is set explicitly on every document: ``cls.env`` runs
        as SUPERUSER here, and the ``customer_payment_import_internal_
        user_rule`` record rule would otherwise hide these fixtures from
        the ``admin`` session that runs the tours.
        """
        super().setUpClass()
        cls.admin = cls.env.ref("base.user_admin")
        cls.cpi_type = cls.env["customer_payment_import_type"].create(
            {
                "name": "TOUR Bank CSV Type",
                "code": "TOURBCT01",
                "file_type": "csv",
                "date_column": "Date",
                "partner_bank_account_column": "Bank Account",
                "amount_column": "Amount",
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "TOUR Bank Journal",
                "type": "general",
                # account.journal.code is size=5 -- keep it short.
                "code": "TOURJ",
            }
        )
        cls.account = cls.env["account.account"].create(
            {
                "name": "TOUR Bank Account",
                "code": "TOURACC1",
                "user_type_id": cls.env.ref(
                    "account.data_account_type_current_assets"
                ).id,
            }
        )
        # Pre-Condition for docs/customer_payment_import/04-confirm.md:
        # status is Draft.
        cls.cpi_confirm = cls.env["customer_payment_import"].create(
            {
                "name": "TOUR-CPI-CONFIRM",
                "type_id": cls.cpi_type.id,
                "journal_id": cls.journal.id,
                "account_id": cls.account.id,
                "user_id": cls.admin.id,
            }
        )
        # Pre-Condition for docs/customer_payment_import/05-approve.md:
        # status is Waiting for Approval.
        cls.cpi_approve = cls.env["customer_payment_import"].create(
            {
                "name": "TOUR-CPI-APPROVE",
                "type_id": cls.cpi_type.id,
                "journal_id": cls.journal.id,
                "account_id": cls.account.id,
                "user_id": cls.admin.id,
            }
        )
        cls.cpi_approve.action_confirm()
        # Pre-Condition for docs/customer_payment_import/10-cancel.md:
        # status allows cancellation (Draft).
        cls.cpi_cancel = cls.env["customer_payment_import"].create(
            {
                "name": "TOUR-CPI-CANCEL",
                "type_id": cls.cpi_type.id,
                "journal_id": cls.journal.id,
                "account_id": cls.account.id,
                "user_id": cls.admin.id,
            }
        )
        cls.cancel_reason = cls.env["base.cancel_reason"].create(
            {
                "name": "TOUR Cancel Reason",
                "code": "TOURCR01",
                "global_use": True,
            }
        )
        # Pre-Condition for docs/customer_payment_import/12-restart.md:
        # status is Cancelled or Rejected. Rejected is reached through
        # action_reject_approval, cheaper to set up than a full
        # confirm/queue-cancel/queue-processing cycle to Cancelled.
        cls.cpi_restart = cls.env["customer_payment_import"].create(
            {
                "name": "TOUR-CPI-RESTART",
                "type_id": cls.cpi_type.id,
                "journal_id": cls.journal.id,
                "account_id": cls.account.id,
                "user_id": cls.admin.id,
            }
        )
        cls.cpi_restart.with_user(cls.admin).action_confirm()
        # approval.approval records created by action_confirm() are read
        # by action_reject_approval() in the same transaction, and the
        # cached ``reject_ok`` policy value (computed while the record
        # was still Draft, before any approver was assigned) would
        # otherwise be reused -- invalidate the cache so it sees them
        # (same pattern used by ssi_employee_external_assignment_
        # agreement's test_ui_employee_external_assignment_agreement.py).
        cls.cpi_restart.invalidate_cache()
        cls.cpi_restart.with_user(cls.admin).action_reject_approval()
        # ``_action_approval`` (ssi_multiple_approval_mixin) silently does
        # nothing if the acting user is not an active approver -- assert
        # the transition actually happened instead of trusting the call.
        assert (
            cls.cpi_restart.state == "reject"
        ), "action_reject_approval() did not move TOUR-CPI-RESTART to reject"

    def test_create(self):
        """Run the create tour for ``customer_payment_import``.

        IK: docs/customer_payment_import/01-create.md
        """
        self.start_tour(
            "/web",
            "ssi_customer_payment_import_customer_payment_import_create",
            login="admin",
        )

    def test_confirm(self):
        """Run the confirm tour for ``customer_payment_import``.

        IK: docs/customer_payment_import/04-confirm.md
        """
        self.start_tour(
            "/web",
            "ssi_customer_payment_import_customer_payment_import_confirm",
            login="admin",
        )

    def test_approve(self):
        """Run the approve tour for ``customer_payment_import``.

        IK: docs/customer_payment_import/05-approve.md
        """
        self.start_tour(
            "/web",
            "ssi_customer_payment_import_customer_payment_import_approve",
            login="admin",
        )

    def test_cancel(self):
        """Run the cancel tour for ``customer_payment_import``.

        IK: docs/customer_payment_import/10-cancel.md
        """
        self.start_tour(
            "/web",
            "ssi_customer_payment_import_customer_payment_import_cancel",
            login="admin",
        )

    def test_restart(self):
        """Run the restart tour for ``customer_payment_import``.

        IK: docs/customer_payment_import/12-restart.md
        """
        self.start_tour(
            "/web",
            "ssi_customer_payment_import_customer_payment_import_restart",
            login="admin",
        )
