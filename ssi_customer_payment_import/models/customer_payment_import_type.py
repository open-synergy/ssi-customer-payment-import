# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


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
    partner_bank_account_column = fields.Char(
        string="Partner Bank Account Column",
        required=True,
        help=(
            "Column name (or 0-based index if No Header Line is checked) "
            "containing the counterparty bank account number. Used to identify "
            "the paying customer by matching it against res.partner.bank."
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

    def _get_column_delimiter_character(self):
        self.ensure_one()
        return {
            "comma": ",",
            "semicolon": ";",
            "tab": "\t",
            "pipe": "|",
            "space": " ",
        }.get(self.delimiter, ",")
