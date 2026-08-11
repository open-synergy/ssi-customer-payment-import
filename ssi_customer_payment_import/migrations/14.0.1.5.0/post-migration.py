# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
# Migration: 14.0.1.4.1 -> 14.0.1.5.0
#
# Changes: ``state`` and ``queue_job_id`` on customer_payment_import.data
#          were added after this module had already been used in
#          production. Upgrading the module filled the new columns with
#          their default value ('draft') on every pre-existing row --
#          including rows whose payment was already created and whose
#          queue job had already finished. This backfills both columns so
#          pre-existing rows carry the state they should already have,
#          without requiring manual correction after every upgrade.

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def _set_done_for_rows_with_payment(cr):
    """Mark pre-existing rows as ``done`` when they already have a payment.

    Plain SQL: no compute/relation needs to be triggered here. Only rows
    still holding the post-upgrade default (``state='draft'``) are
    touched, so running the upgrade twice does not change the result.
    Rows in ``ignored`` state are never matched by this ``WHERE`` clause.

    :param cr: database cursor
    :return: ``None``
    """
    cr.execute(
        """
        UPDATE customer_payment_import_data
        SET state = 'done'
        WHERE state = 'draft'
          AND payment_id IS NOT NULL
        """
    )
    _logger.info(
        "customer_payment_import.data: marked %s pre-existing row(s) as "
        "'done' (payment already linked).",
        cr.rowcount,
    )


def _backfill_queue_job_id_and_error_state(env):
    """Match pre-existing draft rows to their queue job and fix their
    state.

    For every ``customer_payment_import`` document still holding a
    ``done_queue_job_batch_id`` (documents already reached ``done``
    have this field cleared, see
    ``mixin.transaction_queue_done._disconnect_done_batch``), map that
    batch's jobs -- restricted to the document's own batch, never the
    whole ``queue.job`` table -- to the data lines they process via
    ``queue.job.records``. ``records`` is a ``JobSerialized`` field, so
    it cannot be used in a ``search()`` domain; the match has to happen
    in Python.

    Only lines still in ``draft`` are considered, matching
    ``_set_done_for_rows_with_payment`` and leaving ``ignored`` rows
    untouched. For every matched (job, line) pair: fill
    ``queue_job_id`` when still empty, and when the job is ``failed``,
    write ``state='error'`` with ``error_message`` taken from the
    job's ``exc_info``. Draft lines whose job neither finished nor
    failed are left as ``draft``, with only ``queue_job_id`` filled in.
    Running the upgrade twice does not change the result: a line no
    longer in ``draft`` (already turned ``error``) is no longer
    matched, and a line with ``queue_job_id`` already set is not
    written again unless its job just failed.

    :param env: ``api.Environment`` (superuser)
    :return: ``None``
    """
    imports = env["customer_payment_import"].search(
        [("done_queue_job_batch_id", "!=", False)]
    )
    matched = 0
    marked_error = 0
    for import_document in imports:
        jobs = import_document.done_queue_job_batch_id.job_ids
        if not jobs:
            continue
        draft_lines_by_id = {
            line.id: line for line in import_document.data_ids if line.state == "draft"
        }
        if not draft_lines_by_id:
            continue
        for job in jobs:
            for record in job.records:
                if record._name != "customer_payment_import.data":
                    continue
                line = draft_lines_by_id.get(record.id)
                if line is None:
                    continue
                vals = {}
                if not line.queue_job_id:
                    vals["queue_job_id"] = job.id
                if job.state == "failed":
                    vals["state"] = "error"
                    vals["error_message"] = job.exc_info
                if vals:
                    line.write(vals)
                    matched += 1
                    if vals.get("state") == "error":
                        marked_error += 1
    _logger.info(
        "customer_payment_import.data: backfilled queue_job_id/state on "
        "%s row(s) (%s marked 'error').",
        matched,
        marked_error,
    )


def migrate(cr, version):
    """Entry point run by Odoo when upgrading this module.

    No-op on a fresh install (``version`` falsy). See
    ``_set_done_for_rows_with_payment`` and
    ``_backfill_queue_job_id_and_error_state`` for what each step does.

    :param cr: database cursor
    :param version: previously installed module version, or a falsy
        value on a fresh install
    :return: ``None``
    """
    if not version:
        return
    _set_done_for_rows_with_payment(cr)
    env = api.Environment(cr, SUPERUSER_ID, {})
    _backfill_queue_job_id_and_error_state(env)
