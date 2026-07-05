# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Customer Payment Import",
    "version": "14.0.1.0.0",
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
    ],
    "data": [
        # Security - module categories
        "security/ir_module_category/customer_payment_import.xml",
        # Security - groups
        "security/res_groups/customer_payment_import_type.xml",
        # Security - access
        "security/ir_model_access/customer_payment_import_type.xml",
        # Views
        "views/customer_payment_import_type_views.xml",
    ],
    "demo": [
        "demo/customer_payment_import_type_demo.xml",
    ],
    "images": [],
}
