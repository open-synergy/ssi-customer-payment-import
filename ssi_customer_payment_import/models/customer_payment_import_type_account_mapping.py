# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CustomerPaymentImportTypeAccountMapping(models.Model):
    """
    Detail line of Customer Payment Import Type.

    One line binds a single usage value -- as written in the Usage
    Column of the bank file -- to the destination account the customer
    payment created from that row must land on. This lets one bank
    statement file feed several receivable accounts (e.g. tuition fees
    against Enrollment Receivable, entrance fees against Admission
    Receivable) without splitting the file per usage by hand.
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
    usage_value = fields.Char(
        string="Usage Value",
        required=True,
        help=(
            "Value expected in the Usage Column of the import file. "
            "Matching is case-insensitive and ignores leading and "
            "trailing spaces on both sides."
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
            "usage value matches this line."
        ),
    )

    @api.model
    def _normalize_usage_value(self, value):
        """Return the comparable form of a usage value.

        Both sides of a usage comparison go through this method, so
        that the value read from the file and the value configured on
        the mapping line are matched without regard to surrounding
        whitespace or letter case.

        :param value: raw usage value, of any type
        :return: ``str`` stripped and case-folded; ``""`` when
            ``value`` is empty or ``False``
        """
        return str(value or "").strip().casefold()

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

    @api.constrains("type_id", "usage_value")
    def _check_duplicate_usage_value(self):
        """Reject two mapping lines sharing one usage on a Type.

        Uniqueness is enforced on the normalized form (stripped and
        case-folded), because that is the form used when resolving a
        file row -- two lines differing only by case or padding would
        otherwise make the resolution order decide the account.

        Raises ``ValidationError`` when
        ``_check_duplicate_usage_value_condition`` fails.
        """
        for record in self:
            if not record._check_duplicate_usage_value_condition():
                error_message = (
                    _(
                        """
Context: Saving customer payment import type account mapping
Type: %s
Problem: Usage value '%s' is already mapped on this type
Solution: Remove the duplicate mapping line, or change its usage value
          (matching ignores letter case and surrounding spaces)"""
                    )
                    % (
                        record.type_id.display_name,
                        record.usage_value,
                    )
                )
                raise ValidationError(error_message)

    def _check_duplicate_usage_value_condition(self):
        """Return whether this line's usage is unique on its Type.

        :return: ``True`` when no sibling mapping line of the same Type
            normalizes to the same usage value
        """
        self.ensure_one()
        normalized = self._normalize_usage_value(self.usage_value)
        siblings = self.type_id.account_mapping_ids - self
        for sibling in siblings:
            if self._normalize_usage_value(sibling.usage_value) == normalized:
                return False
        return True
