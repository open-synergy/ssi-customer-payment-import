# Deactivate Customer Payment Import Type

> **Module:** ssi_customer_payment_import
> **Model:** `customer_payment_import_type`
> **Menu:** Financial Accounting > Configuration > Customer Payment Import Types
> **Actor:** user in group *Customer Payment Import Type*
> **Active:** `true` → `false`
> **Requires:** `01-create`

## Pre-Condition

- **Record:** The record is currently active.
- **Access:** User is in group *Customer Payment Import Type*.

## Flow

1. Open the **Financial Accounting > Configuration > Customer Payment Import Types** menu.
2. Select one or more records to deactivate (check the checkbox).
3. Click **Action** > **Archive**.
4. Click **OK** to confirm.

## Post-Condition

- The records are archived and no longer appear in the default list view.
- The type can no longer be selected on the **Type** field of a new Customer Payment
  Import document.
- Existing Customer Payment Import documents that already use this type are not
  affected.
