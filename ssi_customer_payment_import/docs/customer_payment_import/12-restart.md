# Restart Customer Payment Import

> **Module:** ssi_customer_payment_import
> **Model:** `customer_payment_import`
> **Menu:** Financial Accounting > Account Receivable > Customer Payment Imports
> **Actor:** user in group *Customer Payment Import — Validator*
> **State:** `cancel` | `reject` → `draft`
> **Requires:** `10-cancel`

## Pre-Condition

- **Record:** Status is **Cancelled** or **Rejected**.
- **Config:** An active `policy.template` grants `restart_ok` for that state to the
  actor's group.
- **Access:** User is in group *Customer Payment Import — Validator*.

## Flow

1. Open the **Financial Accounting > Account Receivable > Customer Payment Imports**
   menu.
2. Open the record to restart.
3. Click the **Restart** button.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- Status returns to **Draft**.
- All approval records are removed and the approval template is cleared. A later
  Confirm starts the approval process from the beginning.
- Existing Import Data lines are not removed by the restart itself.
