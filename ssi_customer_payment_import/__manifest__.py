# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Customer Payment Import",
    "version": "14.0.1.5.0",
    "website": "https://simetri-sinergi.id",
    "author": "OpenSynergy Indonesia, PT. Simetri Sinergi Indonesia",
    "contributors": [
        "Andhitia Rama <andhitia.r@gmail.com>",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "depends": [
        "account",
        "ssi_master_data_mixin",
        "ssi_m2o_configurator_mixin",
        "ssi_financial_accounting",
        "ssi_web_widget_json",
        "ssi_transaction_confirm_mixin",
        "ssi_transaction_queue_done_mixin",
        "ssi_transaction_queue_cancel_mixin",
        "queue_job_batch",
        "base_automation",
    ],
    "external_dependencies": {
        "python": ["openpyxl"],
    },
    "data": [
        # Security - module categories
        "security/ir_module_category/customer_payment_import.xml",
        # Security - groups
        "security/res_groups/customer_payment_import_type.xml",
        "security/res_groups/customer_payment_import.xml",
        # Security - access
        "security/ir_model_access/customer_payment_import_type.xml",
        "security/ir_model_access/customer_payment_import.xml",
        "security/ir_model_access/ignore_customer_payment_import_error.xml",
        "security/ir_model_access/ignore_customer_payment_import_data.xml",
        "security/ir_model_access/edit_customer_payment_import_data.xml",
        # Security - rules
        "security/ir_rule/customer_payment_import.xml",
        # Sequence & templates
        "ir_sequence/customer_payment_import.xml",
        "sequence_template/customer_payment_import.xml",
        "approval_template/customer_payment_import.xml",
        "policy_template/customer_payment_import.xml",
        # Queue automation
        "data/ir_actions_server_data.xml",
        "data/base_automation_data.xml",
        # Wizards
        "wizards/ignore_customer_payment_import_error_views.xml",
        "wizards/ignore_customer_payment_import_data_views.xml",
        "wizards/edit_customer_payment_import_data_views.xml",
        # Views
        "views/customer_payment_import_type_views.xml",
        "views/customer_payment_import_views.xml",
    ],
    "demo": [
        "demo/customer_payment_import_type_demo.xml",
    ],
    "images": [],
}
