# Auto-Done Customer Payment Import

> **Module:** ssi_customer_payment_import\
> **Model:** `customer_payment_import`\
> **Menu:** Financial Accounting > Account Receivable > Customer Payment Imports\
> **Actor:** System (triggered automatically, no user action)\
> **State:** `queue_done` → `done`\
> **Requires:** `05-approve`

## Pre-Condition

- **Record:** Status is **Queue Done**.
- **Record:** Every Import Data line has left the **Draft**/**Error** state (each line
  is **Done** or **Ignored**) — the queue jobs enqueued when the import reached **Queue
  Done** (see `05-approve`) have all finished, one job per Import Data line.

## Flow

This transition has no user-facing step, so it does not start from a menu. It is
triggered automatically by a `base.automation` rule (`customer_payment_import_done`)
that fires whenever this record is written while its "Done" queue job batch status
equals **Finished**. The automation calls `action_recompute_queue_done_result()`, which
re-evaluates the job batch and, once no Import Data line is left **Draft**/**Error**,
moves the record to **Done**.

If any Import Data line is still in the **Error** state when the batch finishes, the
import stays in **Queue Done** — resolve the errored lines (retry or ignore them) so the
batch can be recomputed and the import can reach **Done**.

## Post-Condition

- Status changes to **Done**.
- The document number is generated from the sequence configured for this model, since
  numbering happens on reaching **Done**.
