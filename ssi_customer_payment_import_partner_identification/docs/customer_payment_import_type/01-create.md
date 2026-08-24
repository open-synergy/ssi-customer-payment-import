# Create Customer Payment Import Type

> **Module:** ssi_customer_payment_import_partner_identification **Extends:**
> ssi_customer_payment_import — model `customer_payment_import_type`, aksi `01-create`

## Additional Fields

When this module is installed, **Partner Matching Method** (on the **Column Mapping**
tab) gains a new choice, **Partner Identification**, plus two fields that appear right
after it, visible only when **Partner Matching Method** is set to **Partner
Identification**:

- **Partner Identification Column** _(required if **Partner Matching Method** is
  **Partner Identification**)_: column name (or 0-based index when **No Header Line** is
  checked) that contains the identification number used to identify the paying customer,
  matched against the partner's registered ID Numbers.
- **Partner Identification Category** _(required if **Partner Matching Method** is
  **Partner Identification**)_: the ID Number category (e.g. Student Number) that
  **Partner Identification Column** values are matched against.

## Modified Validation

- Saving the record fails with an error if **Partner Matching Method** is **Partner
  Identification** and either **Partner Identification Column** or **Partner
  Identification Category** is left empty.
