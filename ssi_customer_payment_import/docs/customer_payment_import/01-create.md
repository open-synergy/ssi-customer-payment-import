# Create Customer Payment Import

> **Module:** ssi_customer_payment_import
> **Model:** `customer_payment_import`
> **Menu:** Financial Accounting > Account Receivable > Customer Payment Imports
> **Actor:** user in group *Customer Payment Import — User*
> **State:** `—` → `draft`
> **Inline Actions:** `action_load_data` (Load Data)

## Pre-Condition

- **Data:** At least one active **Customer Payment Import Type** exists.
- **Access:** User is in group *Customer Payment Import — User*.

## Flow

1. Open the **Financial Accounting > Account Receivable > Customer Payment Imports**
   menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the required fields:
   - **Type**: the Customer Payment Import Type that determines the file format and
     allowed Journals/Accounts.
   - **Journal**: journal used to create the resulting customer payments, restricted
     to the Journals allowed by **Type**.
   - **Date**: defaults to today; change if needed.
4. On the header, fill in **Account** (destination account for the resulting customer
   payments) unless **Type** has a **Usage Column** configured — in that case the
   **Account** field is hidden and the destination account is resolved per row instead.
5. Upload the bank file on **Import File**.
6. On the **Import Data** tab, click **Load Data** to read **Import File** and create
   one **Import Data** line per row. You may re-click **Load Data** after replacing
   **Import File** — this deletes the existing Import Data lines and reloads them from
   the new file. Data cannot be reviewed or turned into customer payments until this
   step is done.
7. Click **Save**.

## Post-Condition

- A new record is created in **Draft** status.
- The **Import Data** tab lists one line per row read from the file, with counters for
  **# Data**, **# Done**, **# Error**, and **# Ignored**.
