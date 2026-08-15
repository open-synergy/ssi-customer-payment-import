# Create Customer Payment Import

> **Module:** ssi_customer_payment_import_operating_unit
>
> **Extends:** ssi_customer_payment_import — model `customer_payment_import`, aksi
> `01-create`

## Additional Pre-Condition

- **Config:** Group `operating_unit.group_multi_operating_unit` is active — the
  **Operating Unit** field described below is only visible when this group is enabled.

## Additional Fields

When this module is installed, the create form gains one optional field:

- **Operating Unit**: The operating unit that owns this record. Automatically filled
  from the current user's default operating unit. Change if needed. Visible only when
  group `operating_unit.group_multi_operating_unit` is active.

Selecting **Operating Unit** also affects **Journal**:

- **Journal**: the list of allowed Journals is narrowed to those whose Operating Unit(s)
  either is empty (cross-OU journal, always allowed) or contains the selected
  **Operating Unit**. If the currently selected **Journal** no longer matches after
  changing **Operating Unit**, it is automatically cleared and must be re-selected.

## Modified Validation

- Saving the record (create or update) fails with an error if **Journal**'s Operating
  Unit(s) is set and does not contain the document's **Operating Unit**. Either being
  empty passes.

## Modified — Record Visibility

- The Customer Payment Imports list is filtered by operating unit (record rule
  `customer_payment_import_rule_ou`). A user only sees records whose **Operating Unit**
  is one of the operating units assigned to them (group `Operating Unit` under Data
  Ownership). This is not a Flow step.
