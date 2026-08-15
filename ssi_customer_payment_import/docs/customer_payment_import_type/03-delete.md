# Delete Customer Payment Import Type

> **Module:** ssi_customer_payment_import
> **Model:** `customer_payment_import_type`
> **Menu:** Financial Accounting > Configuration > Customer Payment Import Types
> **Actor:** user in group *Customer Payment Import Type*
> **Requires:** `01-create`

## Pre-Condition

- **Record:** The type is not referenced by any existing Customer Payment Import
  document (the **Type** field on those documents is a required, restrict-on-delete
  relation).
- **Access:** User is in group *Customer Payment Import Type*.

## Flow

1. Open the **Financial Accounting > Configuration > Customer Payment Import Types** menu.
2. Select one or more records to delete (check the checkbox).
3. Click **Action** > **Delete**.
4. Click **OK** to confirm.

## Post-Condition

- The selected records are permanently removed from the system.
