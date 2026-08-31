# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CustomerPaymentImportType(models.Model):
    """
    Represents a template algorithm for parsing customer payment files
    exported from a bank (CSV or XLSX), and for configuring which
    journals are allowed when creating an import document of this type.
    """

    _name = "customer_payment_import_type"
    _inherit = ["mixin.master_data", "mixin.many2one_configurator"]
    _description = "Customer Payment Import Type"

    # --- File format ---

    file_type = fields.Selection(
        string="File Type",
        selection=[
            ("csv", "CSV"),
            ("xlsx", "XLSX"),
        ],
        required=True,
        default="csv",
        help="File format that this type is able to parse.",
    )
    file_encoding = fields.Selection(
        string="Encoding",
        selection=[
            ("utf-8", "UTF-8"),
            ("utf-8-sig", "UTF-8 (with BOM)"),
            ("utf-16", "UTF-16"),
            ("utf-16-sig", "UTF-16 (with BOM)"),
            ("windows-1252", "Western (Windows-1252)"),
            ("iso-8859-1", "Western (Latin-1 / ISO 8859-1)"),
        ],
        default="utf-8",
        help="Character encoding of the file. Only relevant when File Type = CSV.",
    )
    delimiter = fields.Selection(
        string="Delimiter",
        selection=[
            ("comma", "comma (,)"),
            ("semicolon", "semicolon (;)"),
            ("tab", "tab"),
            ("pipe", "pipe (|)"),
            ("space", "space"),
        ],
        default="comma",
        help="Field delimiter used in the file. Only relevant when File Type = CSV.",
    )
    quotechar = fields.Char(
        string="Text Qualifier",
        size=1,
        default='"',
        help=(
            "Character used to quote fields containing special characters. "
            "Only relevant when File Type = CSV."
        ),
    )
    no_header = fields.Boolean(
        string="No Header Line",
        default=False,
        help=(
            "Check if the file does not contain a header row. When checked, "
            "use column index (0-based) instead of column name in the column "
            "mapping fields below."
        ),
    )
    skip_empty_lines = fields.Boolean(
        string="Skip Empty Lines",
        default=True,
        help="Skip blank rows when parsing the file.",
    )
    offset_row = fields.Integer(
        string="Row Offset",
        default=0,
        help="Number of rows to skip from the top before starting to parse.",
    )
    trailing_offset_row = fields.Integer(
        string="Trailing Row Offset",
        default=0,
        help=(
            "Number of rows to skip from the bottom of the file before "
            "parsing stops. Counted on raw file rows exactly like Row "
            "Offset, so blank rows and the header row are included in "
            "the count."
        ),
    )
    sheet_name = fields.Char(
        string="Sheet Name",
        help=(
            "Name of the sheet to read. Leave empty to use the first sheet. "
            "Only relevant when File Type = XLSX."
        ),
    )

    # --- Column mapping ---

    date_column = fields.Char(
        string="Date Column",
        required=True,
        help=(
            "Column name (or 0-based index if No Header Line is checked) "
            "containing the payment date."
        ),
    )
    date_format = fields.Char(
        string="Date Format",
        default="%Y-%m-%d",
        help="Python strptime format string used to parse the Date Column value.",
    )
    partner_matching_method = fields.Selection(
        string="Partner Matching Method",
        selection=[
            ("bank", "Bank Account"),
        ],
        required=True,
        default="bank",
        help=(
            "Method used to identify the paying customer from each row. "
            "Other modules can add more choices to this Selection through "
            "selection_add."
        ),
    )
    partner_bank_account_column = fields.Char(
        string="Partner Bank Account Column",
        help=(
            "Column name (or 0-based index if No Header Line is checked) "
            "containing the counterparty bank account number. Used to identify "
            "the paying customer by matching it against res.partner.bank when "
            "Partner Matching Method = Bank Account, and/or to resolve the "
            "usage feeding Usage Account Mapping when Usage Matching Method "
            "= From Bank Account Column. Required whenever either of those "
            "two is set to that value."
        ),
    )
    usage_matching_method = fields.Selection(
        string="Usage Matching Method",
        selection=[
            ("bank_account_column", "From Bank Account Column"),
            ("partner_bank", "From Matched Partner's Bank Account"),
            ("none", "No Usage"),
        ],
        required=True,
        default="none",
        help=(
            "Method used to resolve the usage (res.partner.bank.usage_id) "
            "that feeds Usage Account Mapping for each row, independently "
            "of Partner Matching Method. 'From Bank Account Column' reads "
            "it off the bank account found through Partner Bank Account "
            "Column, which then becomes required. 'From Matched Partner's "
            "Bank Account' looks it up on the matched partner's own bank "
            "accounts instead. 'No Usage' disables Usage Account Mapping "
            "for this Type -- saving one with mapping lines configured is "
            "rejected."
        ),
    )
    amount_column = fields.Char(
        string="Amount Column",
        required=True,
        help=(
            "Column name (or 0-based index if No Header Line is checked) "
            "containing the payment amount."
        ),
    )
    amount_format = fields.Selection(
        string="Amount Format",
        selection=[
            ("auto", "Auto (guess separators)"),
            ("manual", "Manual (explicit separators)"),
        ],
        required=True,
        default="auto",
        help=(
            "How the Amount Column value is turned into a number. Auto "
            "guesses the thousand/decimal separators from their relative "
            "position in the text, exactly as before this field existed. "
            "Manual applies Amount Thousand Separator and Amount Decimal "
            "Separator below, and also strips any other character (e.g. "
            "a currency prefix such as 'Rp' or 'IDR')."
        ),
    )
    amount_thousand_separator = fields.Selection(
        string="Amount Thousand Separator",
        selection=[
            ("none", "none"),
            ("dot", "dot (.)"),
            ("comma", "comma (,)"),
            ("space", "space"),
        ],
        default="none",
        help=(
            "Thousand separator used in the Amount Column value. Only "
            "applied when Amount Format = Manual."
        ),
    )
    amount_decimal_separator = fields.Selection(
        string="Amount Decimal Separator",
        selection=[
            ("none", "none (integer amount)"),
            ("dot", "dot (.)"),
            ("comma", "comma (,)"),
        ],
        default="dot",
        help=(
            "Decimal separator used in the Amount Column value. Only "
            "applied when Amount Format = Manual."
        ),
    )
    communication_column = fields.Char(
        string="Communication Column",
        help=(
            "Column name (or 0-based index if No Header Line is checked) "
            "containing the payment memo/communication text, if available."
        ),
    )
    unique_ref_column = fields.Char(
        string="Unique Reference Column",
        help=(
            "Column name (or 0-based index if No Header Line is checked) "
            "containing a unique transaction id from the bank, if available. "
            "Used to prevent duplicate payments from being created."
        ),
    )
    exclude_column = fields.Char(
        string="Exclude Column",
        help=(
            "Column name (or 0-based index if No Header Line is checked) "
            "used to automatically exclude rows from being imported (e.g. "
            "opening/closing balance rows, debit mutation rows, cancelled "
            "rows). Leave empty, together with Exclude Values, to disable "
            "this feature."
        ),
    )
    exclude_values = fields.Char(
        string="Exclude Values",
        help=(
            "Comma-separated list of values that, when found in the "
            "Exclude Column, cause the row to be automatically ignored "
            "(e.g. 'Saldo Awal,Saldo Akhir'). Leave empty, together with "
            "Exclude Column, to disable this feature."
        ),
    )

    # --- Payment options ---

    auto_post = fields.Boolean(
        string="Auto Post",
        default=False,
        help=(
            "If checked, the customer payment created from each data line is "
            "posted automatically. If unchecked, the payment is left in draft "
            "state for manual review."
        ),
    )

    # --- Journal M2O configurator ---

    journal_selection_method = fields.Selection(
        string="Journal Selection Method",
        selection=[
            ("manual", "Manual"),
            ("domain", "Domain"),
            ("code", "Python Code"),
        ],
        default="domain",
        required=True,
        help=(
            "Method used to determine which journals can be selected on an "
            "import document of this type."
        ),
    )
    journal_ids = fields.Many2many(
        string="Journals",
        comodel_name="account.journal",
        relation="rel_customer_payment_import_type_2_account_journal",
        column1="type_id",
        column2="journal_id",
        help=(
            "Manually selected list of allowed journals. Used when Journal "
            "Selection Method = Manual."
        ),
    )
    journal_domain = fields.Text(
        default="[]",
        string="Journal Domain",
        help=(
            "Domain expression evaluated against account.journal to determine "
            "the allowed journals. Used when Journal Selection Method = Domain."
        ),
    )
    journal_python_code = fields.Text(
        default="result = []",
        string="Journal Python Code",
        help=(
            "Python code that must set the `result` variable to a recordset of "
            "account.journal. Used when Journal Selection Method = Python Code."
        ),
    )

    # --- Account M2O configurator ---

    account_selection_method = fields.Selection(
        string="Account Selection Method",
        selection=[
            ("manual", "Manual"),
            ("domain", "Domain"),
            ("code", "Python Code"),
        ],
        default="domain",
        required=True,
        help=(
            "Method used to determine which accounts can be selected on an "
            "import document of this type."
        ),
    )
    account_ids = fields.Many2many(
        string="Accounts",
        comodel_name="account.account",
        relation="rel_customer_payment_import_type_2_account_account",
        column1="type_id",
        column2="account_id",
        help=(
            "Manually selected list of allowed accounts. Used when Account "
            "Selection Method = Manual."
        ),
    )
    account_domain = fields.Text(
        default="[]",
        string="Account Domain",
        help=(
            "Domain expression evaluated against account.account to determine "
            "the allowed accounts. Used when Account Selection Method = Domain."
        ),
    )
    account_python_code = fields.Text(
        default="result = []",
        string="Account Python Code",
        help=(
            "Python code that must set the `result` variable to a recordset of "
            "account.account. Used when Account Selection Method = Python Code."
        ),
    )

    # --- Usage account mapping ---

    account_mapping_ids = fields.One2many(
        string="Usage Account Mappings",
        comodel_name="customer_payment_import_type.account_mapping",
        inverse_name="type_id",
        help=(
            "Per-usage destination accounts. Each line binds one value "
            "of the Usage Column to the account the resulting customer "
            "payment must land on."
        ),
    )

    def _get_account_by_usage(self, usage):
        """Return the account mapped to ``usage`` on this Type.

        An empty or unmapped ``usage`` is not an error condition --
        the caller is expected to fall back to another account.

        :param usage: ``res_partner_bank_usage`` recordset (usually a
            single record, or empty when the paying bank account has
            no usage configured)
        :return: the mapped ``account.account`` record, or an empty
            ``account.account`` recordset when nothing matches
        """
        self.ensure_one()
        if not usage:
            return self.env["account.account"]
        for mapping in self.account_mapping_ids:
            if mapping.usage_id == usage:
                return mapping.account_id
        return self.env["account.account"]

    @api.constrains(
        "amount_format", "amount_thousand_separator", "amount_decimal_separator"
    )
    def _check_amount_separator_conflict(self):
        """Reject a Manual amount format whose two separators collide.

        A Manual amount format where Amount Thousand Separator and
        Amount Decimal Separator are set to the same character makes
        it impossible to tell one apart from the other while
        normalizing a value, so the configuration itself is
        ambiguous regardless of the data being imported.

        Raises ``ValidationError`` when
        ``_check_amount_separator_conflict_condition`` fails.
        """
        for record in self:
            if not record._check_amount_separator_conflict_condition():
                error_message = (
                    _(
                        """
Context: Saving customer payment import type
Type: %s
Problem: Amount Thousand Separator and Amount Decimal Separator are
         both set to '%s'
Solution: Configure two different separators, or set the unused one
          to 'none'"""
                    )
                    % (record.display_name, record.amount_thousand_separator)
                )
                raise ValidationError(error_message)

    def _check_amount_separator_conflict_condition(self):
        """Return whether this Type's amount separator setup is
        self-consistent.

        :return: ``False`` when ``amount_format`` is ``"manual"`` and
            ``amount_thousand_separator`` equals
            ``amount_decimal_separator``; ``True`` otherwise
        """
        self.ensure_one()
        if self.amount_format != "manual":
            return True
        return self.amount_thousand_separator != self.amount_decimal_separator

    @api.constrains("trailing_offset_row")
    def _check_trailing_offset_row(self):
        """Reject a negative Trailing Row Offset.

        Raises ``ValidationError`` when
        ``_check_trailing_offset_row_condition`` fails.
        """
        for record in self:
            if not record._check_trailing_offset_row_condition():
                error_message = (
                    _(
                        """
Context: Saving customer payment import type
Type: %s
Problem: Trailing Row Offset is negative (%s)
Solution: Set Trailing Row Offset to zero or a positive number"""
                    )
                    % (record.display_name, record.trailing_offset_row)
                )
                raise ValidationError(error_message)

    def _check_trailing_offset_row_condition(self):
        """Return whether this Type's Trailing Row Offset is valid.

        :return: ``False`` when ``trailing_offset_row`` is negative;
            ``True`` otherwise
        """
        self.ensure_one()
        return self.trailing_offset_row >= 0

    @api.constrains("partner_matching_method", "partner_bank_account_column")
    def _check_partner_matching_method(self):
        """Reject a Bank Account matching method without its source
        column.

        Raises ``ValidationError`` when
        ``_check_partner_matching_method_condition`` fails.
        """
        for record in self:
            if not record._check_partner_matching_method_condition():
                error_message = (
                    _(
                        """
Context: Saving customer payment import type
Type: %s
Problem: Partner Matching Method is 'Bank Account' but Partner Bank
         Account Column is empty
Solution: Fill in Partner Bank Account Column, or choose a different
          Partner Matching Method"""
                    )
                    % (record.display_name,)
                )
                raise ValidationError(error_message)

    def _check_partner_matching_method_condition(self):
        """Return whether this Type's partner matching setup is
        complete.

        Written as an if/elif dispatcher per ``partner_matching_method``
        value, so a module adding another value through
        ``selection_add`` extends this with its own ``elif`` branch in
        an override, instead of editing the ``"bank"`` branch below.

        :return: ``False`` when ``partner_matching_method`` is
            ``"bank"`` and ``partner_bank_account_column`` is empty;
            ``True`` otherwise
        """
        self.ensure_one()
        if self.partner_matching_method == "bank":
            return bool(self.partner_bank_account_column)
        return True

    @api.constrains("usage_matching_method", "partner_bank_account_column")
    def _check_usage_matching_method(self):
        """Reject a Bank Account Column usage method without its
        source column.

        Raises ``ValidationError`` when
        ``_check_usage_matching_method_condition`` fails.
        """
        for record in self:
            if not record._check_usage_matching_method_condition():
                error_message = (
                    _(
                        """
Context: Saving customer payment import type
Type: %s
Problem: Usage Matching Method is 'From Bank Account Column' but
         Partner Bank Account Column is empty
Solution: Fill in Partner Bank Account Column, or choose a different
          Usage Matching Method"""
                    )
                    % (record.display_name,)
                )
                raise ValidationError(error_message)

    def _check_usage_matching_method_condition(self):
        """Return whether this Type's usage matching setup is
        complete.

        Written as an if/elif dispatcher per ``usage_matching_method``
        value, mirroring
        ``_check_partner_matching_method_condition``, so a module
        adding another value extends this with its own ``elif``
        branch in an override.

        :return: ``False`` when ``usage_matching_method`` is
            ``"bank_account_column"`` and
            ``partner_bank_account_column`` is empty; ``True``
            otherwise
        """
        self.ensure_one()
        if self.usage_matching_method == "bank_account_column":
            return bool(self.partner_bank_account_column)
        return True

    @api.constrains("usage_matching_method", "account_mapping_ids")
    def _check_account_mapping_reachable(self):
        """Reject Usage Account Mapping lines that can never apply.

        Raises ``ValidationError`` when
        ``_check_account_mapping_reachable_condition`` fails.
        """
        for record in self:
            if not record._check_account_mapping_reachable_condition():
                error_message = (
                    _(
                        """
Context: Saving customer payment import type
Type: %s
Problem: Usage Matching Method is 'No Usage' but this Type still has
         Usage Account Mapping line(s)
Solution: Remove the Usage Account Mapping lines, or choose a Usage
          Matching Method other than 'No Usage'"""
                    )
                    % (record.display_name,)
                )
                raise ValidationError(error_message)

    def _check_account_mapping_reachable_condition(self):
        """Return whether this Type's mapping lines can ever apply.

        :return: ``False`` when ``usage_matching_method`` is
            ``"none"`` and ``account_mapping_ids`` is not empty;
            ``True`` otherwise
        """
        self.ensure_one()
        if self.usage_matching_method == "none":
            return not self.account_mapping_ids
        return True

    def _normalize_amount_text(self, value):
        """Normalize a raw amount cell value into a string ``float()``
        can parse.

        When ``amount_format`` is ``"manual"``: every character that
        is not a digit, this Type's configured thousand/decimal
        separator, or a leading ``-`` sign is dropped first (this is
        what removes currency prefixes such as ``Rp``/``IDR`` and
        stray spaces); the thousand separator is then dropped, and
        the decimal separator is turned into ``.``. When
        ``amount_format`` is ``"auto"``, the historical heuristic
        that guesses the separators from their relative position is
        applied unchanged.

        :param value: raw amount cell value (usually a ``str``, but a
            falsy value is tolerated)
        :return: ``str`` ready to be converted with ``float()``
        """
        self.ensure_one()
        text = str(value or "").strip()

        if self.amount_format != "manual":
            text = text.replace(" ", "")
            if "," in text and "." in text:
                if text.rfind(",") > text.rfind("."):
                    text = text.replace(".", "").replace(",", ".")
                else:
                    text = text.replace(",", "")
            elif "," in text:
                text = text.replace(",", ".")
            return text

        separator_character = {
            "none": "",
            "dot": ".",
            "comma": ",",
            "space": " ",
        }
        thousand_character = separator_character[self.amount_thousand_separator]
        decimal_character = separator_character[self.amount_decimal_separator]

        allowed_characters = set("0123456789")
        if thousand_character:
            allowed_characters.add(thousand_character)
        if decimal_character:
            allowed_characters.add(decimal_character)

        sign = "-" if text.startswith("-") else ""
        digits_and_separators = "".join(
            character for character in text if character in allowed_characters
        )
        text = sign + digits_and_separators

        if thousand_character:
            text = text.replace(thousand_character, "")
        if decimal_character:
            text = text.replace(decimal_character, ".")

        return text

    def _get_column_delimiter_character(self):
        """Translate the ``delimiter`` selection into its CSV character.

        :return: the delimiter character; defaults to ``","`` when
            ``delimiter`` is unset or unrecognized
        """
        self.ensure_one()
        return {
            "comma": ",",
            "semicolon": ";",
            "tab": "\t",
            "pipe": "|",
            "space": " ",
        }.get(self.delimiter, ",")

    def _get_exclude_value_tokens(self):
        """Return the Exclude Values tokens used to auto-ignore rows.

        Splits ``exclude_values`` on commas, strips each token, and
        drops empty tokens. Returns an empty list whenever
        ``exclude_column`` or ``exclude_values`` is not configured, so
        that an Exclude Column filled in with Exclude Values left
        empty does not exclude every row whose column happens to be
        blank.

        :return: list of stripped, non-empty ``str`` tokens
        """
        self.ensure_one()
        if not self.exclude_column or not self.exclude_values:
            return []
        return [
            token.strip() for token in self.exclude_values.split(",") if token.strip()
        ]
