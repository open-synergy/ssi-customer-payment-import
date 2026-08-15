# Restart Approval Process — Customer Payment Import

> **Module:** ssi_customer_payment_import
> **Model:** `customer_payment_import`
> **Menu:** Financial Accounting > Account Receivable > Customer Payment Imports
> **Actor:** user in group *Customer Payment Import — Validator*
> **Requires:** `04-confirm`

## Pre-Condition

- **Record:** Status is **Waiting for Approval**.
- **Record:** No `approval.template` currently matches this record (e.g. the standard
  approval template configuration was changed or removed after the record was
  confirmed).
- **Config:** An active `policy.template` grants `restart_approval_ok` for state
  `confirm` to the actor's group.
- **Access:** User is in group *Customer Payment Import — Validator*.

## Flow

1. Open the **Financial Accounting > Account Receivable > Customer Payment Imports**
   menu.
2. Open the record whose approval process is stuck.
3. Click the **Restart Approval Process** button.

## Post-Condition

- The approval template is re-evaluated and, if a matching `approval.template` is now
  found, new approval records are created for it. Status remains **Waiting for
  Approval**.
