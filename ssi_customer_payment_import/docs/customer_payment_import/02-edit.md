# Edit Customer Payment Import

> **Module:** ssi_customer_payment_import\
> **Model:** `customer_payment_import`\
> **Menu:** Financial Accounting > Account Receivable > Customer Payment Imports\
> **Actor:** user in group `Customer Payment Import — User`\
> **Requires:** `01-create`\
> **Inline Actions:** `action_load_data` (Load Data)

## Pre-Condition

- **Record:** Status is **Draft**.
- **Access:** User is in group _Customer Payment Import — User_.

## Flow

1. Open the **Financial Accounting > Account Receivable > Customer Payment Imports**
   menu.
2. Find and open the record to edit.
3. Change the required fields, or replace **Import File** with a different bank file.
4. On the **Import Data** tab, click **Load Data** to reload the Import Data lines from
   the current **Import File** — for example after replacing the file, or after changing
   **Type**. This deletes any existing Import Data lines and re-reads the file. Skipping
   this step after replacing the file leaves the Import Data lines out of sync with the
   uploaded file.
5. Click **Save**.

## Post-Condition

- The record is updated with the new values.
