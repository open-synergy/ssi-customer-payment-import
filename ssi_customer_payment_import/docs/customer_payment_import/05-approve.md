# Approve Customer Payment Import

> **Module:** ssi_customer_payment_import
> **Model:** `customer_payment_import`
> **Menu:** Financial Accounting > Account Receivable > Customer Payment Imports
> **Actor:** user in group *Customer Payment Import — Validator*
> **State:** `confirm` → `queue_done`
> **Requires:** `04-confirm`

## Pre-Condition

- **Record:** Status is **Waiting for Approval**.
- **Config:** An active `policy.template` grants `approve_ok` to the actor's group.
- **Access:** User is registered as an approver on the approval level that is currently
  **pending**. The standard approval template for this model has a single level open
  to any user in group *Customer Payment Import — Validator*.

## Flow

1. Open the **Financial Accounting > Account Receivable > Customer Payment Imports**
   menu.
2. Open the record to approve.
3. Click the **Approve** button.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- If there are still pending approval levels, status remains **Waiting for Approval**
  and the next level becomes pending.
- If all approval levels are fulfilled, the import automatically moves to **Queue Done**
  status (there is no separate user action for this transition), and one background job
  per Import Data line is enqueued to create the corresponding Customer Payment. Once
  every job has finished, the import automatically moves to **Done** — see
  `09-auto-done`.
