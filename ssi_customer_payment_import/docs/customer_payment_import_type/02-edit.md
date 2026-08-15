# Edit Customer Payment Import Type

> **Module:** ssi_customer_payment_import
> **Model:** `customer_payment_import_type`
> **Menu:** Financial Accounting > Configuration > Customer Payment Import Types
> **Actor:** user in group *Customer Payment Import Type*
> **Requires:** `01-create`

## Pre-Condition

- **Access:** User is in group *Customer Payment Import Type*.

## Flow

1. Open the **Financial Accounting > Configuration > Customer Payment Import Types** menu.
2. Find and open the record to edit.
3. Change the required fields.
4. If **Usage Column** is filled in, ensure the **Usage Account Mapping** tab still has
   at least one line — saving with **Usage Column** filled in and no mapping line is
   rejected.
5. Click **Save**.

## Post-Condition

- The record is updated with the new values.
- Customer Payment Import documents already created from this type are not
  retroactively changed; the new settings apply the next time this type is used to
  load data.
