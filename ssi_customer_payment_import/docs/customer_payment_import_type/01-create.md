# Create Customer Payment Import Type

> **Module:** ssi_customer_payment_import\
> **Model:** `customer_payment_import_type`\
> **Menu:** Financial Accounting > Configuration > Customer Payment Import Types\
> **Actor:** user in group `Customer Payment Import Type`

## Pre-Condition

- **Access:** User is in group _Customer Payment Import Type_.

## Flow

1. Open the **Financial Accounting > Configuration > Customer Payment Import Types**
   menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the required fields:
   - **Name**: label used to identify this import type.
   - **Code**: unique identifier for this import type. Fill with **/** if no particular
     code is needed.
   - **File Type**: file format this type is able to parse (**CSV** or **XLSX**).
   - **Date Column**: column name (or 0-based index when **No Header Line** is checked)
     that contains the payment date.
   - **Partner Bank Account Column**: column name containing the counterparty bank
     account number, used to identify the paying customer.
   - **Amount Column**: column name containing the payment amount.
4. On the **File Format** tab, review **Encoding**, **Delimiter**, **Text Qualifier**,
   **Sheet Name**, **No Header Line**, **Skip Empty Lines**, and **Row Offset** to match
   the bank file this type will parse.
5. On the **Column Mapping** tab, optionally fill in **Communication Column**, **Unique
   Reference Column**, **Exclude Column**, and **Exclude Values**.
6. On the **Payment Option** tab, set **Auto Post** if the resulting customer payments
   should be posted automatically instead of left in draft.
7. On the **Journal Configuration** tab, set **Journal Selection Method** and fill in
   **Journals**, **Journal Domain**, or **Journal Python Code** accordingly, to
   determine which journals are allowed on an import document of this type.
8. On the **Account Configuration** tab, set **Account Selection Method** and fill in
   **Accounts**, **Account Domain**, or **Account Python Code** accordingly, to
   determine which accounts are allowed.
9. On the **Usage Account Mapping** tab, optionally add lines mapping a **Usage** (from
   the bank account usage master data, `res_partner_bank_usage`) to an **Account** — an
   import document using this type will resolve the destination account per row from the
   usage configured on the paying customer's bank account (`res.partner.bank`
   **Usage**), falling back to the document-level Account when the bank account has no
   usage, or its usage is not mapped here.
10. Click **Save**.

## Post-Condition

- A new **Customer Payment Import Type** record is created and active.
- The type becomes selectable on the **Type** field of a Customer Payment Import
  document.
