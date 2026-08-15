# Activate Customer Payment Import Type

> **Module:** ssi_customer_payment_import\
> **Model:** `customer_payment_import_type`\
> **Menu:** Financial Accounting > Configuration > Customer Payment Import Types\
> **Actor:** user in group `Customer Payment Import Type`\
> **Active:** `false` → `true`\
> **Requires:** `04-deactivate`

## Pre-Condition

- **Record:** The record is currently archived.
- **Access:** User is in group _Customer Payment Import Type_.

## Flow

1. Open the **Financial Accounting > Configuration > Customer Payment Import Types**
   menu.
2. Enable the **Archived** filter in the search bar.
3. Select one or more records to reactivate (check the checkbox).
4. Click **Action** > **Unarchive**.

## Post-Condition

- The records are restored and appear again in the default list view.
- The type can be selected again on the **Type** field of a new Customer Payment Import
  document.
