# Delete Customer Payment Import

> **Module:** ssi_customer_payment_import\
> **Model:** `customer_payment_import`\
> **Menu:** Financial Accounting > Account Receivable > Customer Payment Imports\
> **Actor:** user in group `Customer Payment Import — User`\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** Status is **Draft**.
- **Record:** Document number is still **/** (not yet generated).
- **Access:** User is in group _Customer Payment Import — User_.

## Flow

1. Open the **Financial Accounting > Account Receivable > Customer Payment Imports**
   menu.
2. Select one or more records to delete (check the checkbox).
3. Click **Action** > **Delete**.
4. Click **OK** to confirm.

## Post-Condition

- The selected records, together with their Import Data lines, are permanently removed
  from the system.
