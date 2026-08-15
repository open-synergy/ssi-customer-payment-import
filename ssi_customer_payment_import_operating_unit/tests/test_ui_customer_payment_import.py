# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase -- BUKAN HttpCase. 14.0's HttpCase has no cls.env in
# setUpClass (see odoo-development-ui-test skill, structure-and-runner.md).
from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiCustomerPaymentImport(HttpSavepointCase):
    """Tour test for the create-time Operating Unit field."""

    @classmethod
    def setUpClass(cls):
        """Grant ``admin`` the multi operating unit group.

        Pre-Condition IK: the Operating Unit field is gated by
        ``groups="operating_unit.group_multi_operating_unit"`` in the
        form view -- without membership, the field is never rendered
        and the delta assertion would never find it. ``admin`` also
        needs at least one operating unit assigned so the field has a
        meaningful (non-empty) allowed set. ``admin`` is already a
        member of ``customer_payment_import_validator_group`` (see
        the base module's ``security/res_groups/customer_payment_
        import.xml``), so no extra group is needed to open the menu.
        """
        super().setUpClass()
        cls.user_admin = cls.env.ref("base.user_admin")
        operating_unit_partner = cls.env["res.partner"].create(
            {"name": "Tour CPI OU Partner"}
        )
        cls.operating_unit = cls.env["operating.unit"].create(
            {
                "name": "Tour CPI Operating Unit",
                "code": "TCPIOU",
                "partner_id": operating_unit_partner.id,
            }
        )
        cls.env.ref("operating_unit.group_multi_operating_unit").sudo().write(
            {"users": [(4, cls.user_admin.id)]}
        )
        cls.user_admin.sudo().write(
            {
                "assigned_operating_unit_ids": [(4, cls.operating_unit.id)],
                "default_operating_unit_id": cls.operating_unit.id,
            }
        )

    def test_create(self):
        """Run the create tour for ``customer_payment_import``.

        IK: docs/customer_payment_import/01-create.md (E1 delta --
        Additional Fields)
        """
        self.start_tour(
            "/web",
            "ssi_customer_payment_import_operating_unit_customer_payment_import_create",
            login="admin",
        )
