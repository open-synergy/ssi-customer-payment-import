# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
# Migration: 14.0.1.10.0 -> 14.0.1.11.0
#
# Changes: Usage resolution used to be tied to partner_matching_method --
#          only the "bank" branch ever returned a usage, so a Type using
#          any other partner matching method could never make Usage
#          Account Mapping apply. It is now driven by its own field,
#          usage_matching_method, independent of partner_matching_method.
#          This is a "pre" script (not "post") because
#          usage_matching_method is required=True: the column must
#          already hold a value on every row before the ORM applies the
#          NOT NULL constraint while loading the field.

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _add_usage_matching_method_column(cr):
    """Add the ``usage_matching_method`` column if it does not exist.

    Idempotent: safe to run again on a database where a previous,
    interrupted run of this script already added the column.

    :param cr: database cursor
    :return: ``None``
    """
    openupgrade.logged_query(
        cr,
        """
        ALTER TABLE customer_payment_import_type
        ADD COLUMN IF NOT EXISTS usage_matching_method VARCHAR
        """,
    )


def _fill_usage_matching_method(cr):
    """Backfill ``usage_matching_method`` on every pre-existing Type.

    A Type whose ``partner_matching_method`` is ``"bank"`` gets
    ``"bank_account_column"`` -- this preserves the only usage
    resolution behaviour that existed before this field: reading the
    usage off the same bank account ``_find_partner`` matched. Every
    other Type gets ``"none"``, so a pre-existing Type using another
    partner matching method (e.g. ``"identification"``) does not
    suddenly start requiring ``partner_bank_account_column``. A Type
    that already carries Usage Account Mapping lines which could
    never actually apply is left as-is here; the new "mapping
    unreachable" constraint then rejects its next save, forcing a
    conscious choice instead of silently changing behaviour.

    :param cr: database cursor
    :return: ``None``
    """
    rows = openupgrade.logged_query(
        cr,
        """
        UPDATE customer_payment_import_type
        SET usage_matching_method = 'bank_account_column'
        WHERE partner_matching_method = 'bank'
          AND usage_matching_method IS NULL
        """,
    )
    _logger.info(
        "customer_payment_import_type: set usage_matching_method = "
        "'bank_account_column' on %s pre-existing row(s).",
        rows,
    )
    rows = openupgrade.logged_query(
        cr,
        """
        UPDATE customer_payment_import_type
        SET usage_matching_method = 'none'
        WHERE usage_matching_method IS NULL
        """,
    )
    _logger.info(
        "customer_payment_import_type: set usage_matching_method = "
        "'none' on %s pre-existing row(s).",
        rows,
    )


@openupgrade.migrate()
def migrate(env, version):
    """Add and backfill ``usage_matching_method`` before it becomes
    ``required``.

    See ``_add_usage_matching_method_column`` and
    ``_fill_usage_matching_method`` for what each step does.

    :param env: the migration environment
    :param version: the version being migrated to (unused)
    :return: ``None``
    """
    cr = env.cr
    _add_usage_matching_method_column(cr)
    _fill_usage_matching_method(cr)
