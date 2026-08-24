# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
# Migration: 14.0.1.9.0 -> 14.0.1.10.0
#
# Changes: The contra account per import row used to be resolved from a
#          free-text "Usage Column" read out of the bank file, matched
#          against a free-text usage_value on each Usage Account
#          Mapping line. Both fields are replaced by a proper
#          usage_id (Many2one res_partner_bank_usage) -- on the
#          mapping line, matching the usage now configured on the
#          paying customer's res.partner.bank record instead of a
#          column that bank mutation files never actually carried.
#          This backfills usage_id on every pre-existing mapping line
#          by matching its old usage_value text against
#          res_partner_bank_usage.name, drops lines that find no
#          match (their key was a file column value that never
#          existed, so it cannot be preserved), then drops both
#          obsolete columns.

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _fill_usage_id_from_usage_value(cr):
    """Backfill ``usage_id`` on pre-existing Usage Account Mapping
    lines by matching their old ``usage_value`` text against
    ``res_partner_bank_usage.name``.

    The comparison is case-insensitive and ignores surrounding
    whitespace on both sides, mirroring the matching behaviour the
    removed ``usage_value``/``usage_column`` mechanism used to have.

    :param cr: database cursor
    :return: ``None``
    """
    rows = openupgrade.logged_query(
        cr,
        """
        UPDATE customer_payment_import_type_account_mapping AS mapping
        SET usage_id = usage.id
        FROM res_partner_bank_usage AS usage
        WHERE mapping.usage_id IS NULL
          AND TRIM(LOWER(mapping.usage_value)) = TRIM(LOWER(usage.name))
        """,
    )
    _logger.info(
        "customer_payment_import_type.account_mapping: matched %s "
        "pre-existing row(s) to a res_partner_bank_usage by name.",
        rows,
    )


def _delete_unmatched_mapping_lines(cr):
    """Delete mapping lines whose ``usage_value`` matched no
    ``res_partner_bank_usage``, logging each one before it is
    removed.

    Their key was a value read from a file column that never
    actually existed in any bank mutation file, so it cannot be
    preserved -- the Type must be reconfigured with a proper
    ``res_partner_bank_usage`` after the upgrade.

    :param cr: database cursor
    :return: ``None``
    """
    cr.execute(
        """
        SELECT id, type_id, usage_value
        FROM customer_payment_import_type_account_mapping
        WHERE usage_id IS NULL
        """
    )
    unmatched = cr.fetchall()
    for mapping_id, type_id, usage_value in unmatched:
        _logger.warning(
            "customer_payment_import_type.account_mapping: deleting "
            "mapping line id=%s (type_id=%s) -- usage_value %r matched "
            "no res_partner_bank_usage. Reconfigure the Usage Account "
            "Mapping on this Type after the upgrade.",
            mapping_id,
            type_id,
            usage_value,
        )
    if not unmatched:
        return
    openupgrade.logged_query(
        cr,
        """
        DELETE FROM customer_payment_import_type_account_mapping
        WHERE usage_id IS NULL
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    """Backfill ``usage_id`` from the removed ``usage_value``/
    ``usage_column`` fields, then drop both obsolete columns.

    See ``_fill_usage_id_from_usage_value`` and
    ``_delete_unmatched_mapping_lines`` for what each step does.

    :param env: the migration environment
    :param version: the version being migrated to (unused)
    :return: ``None``
    """
    cr = env.cr
    _fill_usage_id_from_usage_value(cr)
    _delete_unmatched_mapping_lines(cr)
    openupgrade.drop_columns(
        cr,
        [
            ("customer_payment_import_type", "usage_column"),
            ("customer_payment_import_type_account_mapping", "usage_value"),
        ],
    )
