# Reject Customer Payment Import

> **Module:** ssi_customer_payment_import
> **Model:** `customer_payment_import`
> **Menu:** Financial Accounting > Account Receivable > Customer Payment Imports
> **Actor:** user in group *Customer Payment Import — Validator*
> **State:** `confirm` → `reject`
> **Requires:** `04-confirm`

## Pre-Condition

- **Record:** Status is **Waiting for Approval**.
- **Config:** An active `policy.template` grants `reject_ok` to the actor's group.
- **Access:** User is registered as an approver on the approval level that is currently
  pending.

## Flow

1. Open the **Financial Accounting > Account Receivable > Customer Payment Imports**
   menu.
2. Open the record to reject.
3. Click the **Reject** button.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- Status changes to **Rejected**.
