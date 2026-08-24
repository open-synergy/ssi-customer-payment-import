# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CustomerPaymentImportTypeAccountMapping(models.Model):
    """
    Detail line of Customer Payment Import Type.

    One line binds a single ``res_partner_bank_usage`` -- the usage
    configured on the paying customer's bank account -- to the
    destination account the customer payment created from that row
    must land on. This lets one bank statement file feed several
    receivable accounts (e.g. tuition fees against Enrollment
    Receivable, entrance fees against Admission Receivable) without
    splitting the file per usage by hand.
    """

    _name = "customer_payment_import_type.account_mapping"
    _description = "Customer Payment Import Type - Account Mapping"
    _inherit = [
        "mixin.many2one_configurator",
    ]
    _order = "type_id, sequence, id"

    type_id = fields.Many2one(
        string="# Type",
        comodel_name="customer_payment_import_type",
        required=True,
        ondelete="cascade",
        help="The import type this usage-to-account mapping belongs to.",
    )
    sequence = fields.Integer(
        string="Sequence",
        required=True,
        default=5,
        help="Display order of this mapping line within its import type.",
    )
    usage_id = fields.Many2one(
        string="Usage",
        comodel_name="res_partner_bank_usage",
        required=True,
        ondelete="restrict",
        help=(
            "Usage expected on the paying bank account (res.partner.bank "
            "usage_id) for this line to apply."
        ),
    )
    allowed_account_ids = fields.Many2many(
        string="Allowed Accounts",
        comodel_name="account.account",
        compute="_compute_allowed_account_ids",
        store=False,
        compute_sudo=True,
        help="Accounts allowed to be selected, as configured on the Type.",
    )
    account_id = fields.Many2one(
        string="Account",
        comodel_name="account.account",
        required=True,
        ondelete="restrict",
        domain="[('id', 'in', allowed_account_ids)]",
        help=(
            "Destination account used for every import file row whose "
            "paying bank account usage matches this line."
        ),
    )

    @api.depends("type_id")
    def _compute_allowed_account_ids(self):
        """Compute ``allowed_account_ids`` from the Type's M2O
        configurator settings for destination accounts.

        Falls back to every account when ``type_id`` is not set yet --
        the Type's own default is an empty domain, i.e. no
        restriction -- so that an empty domain never silently hides
        every account from the ``account_id`` dropdown.
        """
        obj_account = self.env["account.account"]
        for record in self:
            result = obj_account.search([])
            if record.type_id:
                result = record._m2o_configurator_get_filter(
                    object_name="account.account",
                    method_selection=record.type_id.account_selection_method,
                    manual_recordset=record.type_id.account_ids,
                    domain=record.type_id.account_domain,
                    python_code=record.type_id.account_python_code,
                )
            record.allowed_account_ids = result

    @api.constrains("type_id", "usage_id")
    def _check_duplicate_usage(self):
        """Reject two mapping lines sharing one usage on a Type.

        Raises ``ValidationError`` when
        ``_check_duplicate_usage_condition`` fails.
        """
        for record in self:
            if not record._check_duplicate_usage_condition():
                error_message = (
                    _(
                        """
Context: Saving customer payment import type account mapping
Type: %s
Problem: Usage '%s' is already mapped on this type
Solution: Remove the duplicate mapping line, or change its usage"""
                    )
                    % (
                        record.type_id.display_name,
                        record.usage_id.display_name,
                    )
                )
                raise ValidationError(error_message)

    def _check_duplicate_usage_condition(self):
        """Return whether this line's usage is unique on its Type.

        :return: ``True`` when no sibling mapping line of the same Type
            shares the same ``usage_id``
        """
        self.ensure_one()
        siblings = self.type_id.account_mapping_ids - self
        return self.usage_id not in siblings.mapped("usage_id")
