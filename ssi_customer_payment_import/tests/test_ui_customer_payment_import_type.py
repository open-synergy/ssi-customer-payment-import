# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase -- NOT HttpCase. In 14.0, HttpCase does not set up
# cls.env in setUpClass, and every Pre-Condition here is prepared there.
from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiCustomerPaymentImportType(HttpSavepointCase):
    """Tour tests for the ``customer_payment_import_type`` work
    instructions.
    """

    def test_create(self):
        """Run the create tour for ``customer_payment_import_type``.

        IK: docs/customer_payment_import_type/01-create.md
        """
        self.start_tour(
            "/web",
            "ssi_customer_payment_import_customer_payment_import_type_create",
            login="admin",
        )
