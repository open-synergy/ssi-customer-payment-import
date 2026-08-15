# Auto-Cancel Customer Payment Import

> **Module:** ssi_customer_payment_import
> **Model:** `customer_payment_import`
> **Menu:** Financial Accounting > Account Receivable > Customer Payment Imports
> **Actor:** System (triggered automatically, no user action)
> **State:** `queue_cancel` → `cancel`
> **Requires:** `10-cancel`

## Pre-Condition

- **Record:** Status is **Queue Cancel**.
- **Record:** The queue jobs enqueued when the import reached **Queue Cancel** (see
  `10-cancel`) have all finished, one job per Import Data line that had a linked
  Customer Payment.

## Flow

This transition has no user-facing step, so it does not start from a menu. It is
triggered automatically by a `base.automation` rule (`customer_payment_import_cancel`)
that fires whenever this record is written while its "Cancel" queue job batch status
equals **Finished**. The automation calls `action_recompute_queue_cancel_result()`,
which re-evaluates the job batch and, once it has finished, moves the record to
**Cancelled**.

## Post-Condition

- Status changes to **Cancelled**.
