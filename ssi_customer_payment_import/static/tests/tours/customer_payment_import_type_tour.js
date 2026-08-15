// Copyright 2026 OpenSynergy Indonesia
// Copyright 2026 PT. Simetri Sinergi Indonesia
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define("ssi_customer_payment_import.customer_payment_import_type_tour", function (
    require
) {
    "use strict";

    var tour = require("web_tour.tour");

    // IK: docs/customer_payment_import_type/01-create.md
    tour.register(
        "ssi_customer_payment_import_customer_payment_import_type_create",
        {
            test: true,
            url: "/web",
        },
        [
            // ── Flow 1 — Open the Financial Accounting > Configuration >
            // Customer Payment Import Types menu.
            tour.stepUtils.showAppsMenuItem(),
            {
                content: "Open the Financial Accounting app",
                trigger:
                    '.o_app[data-menu-xmlid="ssi_financial_accounting.menu_root_financial_accounting"]',
            },
            {
                content: "Open the Configuration menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_financial_accounting.menu_financial_accounting_configuration"]',
            },
            {
                content: "Open the Customer Payment Import Types menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_customer_payment_import.customer_payment_import_type_menu"]',
            },
            {
                content: "Customer Payment Import Types list is displayed",
                trigger:
                    ".o_control_panel .breadcrumb-item.active:contains(Customer Payment Import Types)",
                extra_trigger: ".o_list_view",
                run: function () {},
            },
            // ── Flow 2 — Click the New button.
            {
                content: "Click Create",
                trigger: ".o_list_button_add",
                extra_trigger: ".o_list_view",
            },
            {
                content: "Form is open in edit mode",
                trigger: ".o_form_view.o_form_editable",
                run: function () {},
            },
            // ── Flow 3 — Fill in the required fields (Name, File Type,
            // Date Column, Partner Bank Account Column, Amount Column).
            {
                content: "Fill in Name",
                trigger: ".o_field_widget[name='name']",
                extra_trigger: ".o_form_view.o_form_editable",
                run: "text TOUR Bank CSV",
            },
            {
                content: "Open the Column Mapping tab",
                trigger: ".o_notebook .nav-link:contains(Column Mapping)",
            },
            {
                content: "Fill in Date Column",
                trigger: ".o_field_widget[name='date_column']",
                extra_trigger: ".o_form_view.o_form_editable",
                run: "text Date",
            },
            {
                content: "Fill in Partner Bank Account Column",
                trigger: ".o_field_widget[name='partner_bank_account_column']",
                run: "text Bank Account",
            },
            {
                content: "Fill in Amount Column",
                trigger: ".o_field_widget[name='amount_column']",
                run: "text Amount",
            },
            // ── Flow 10 — Click Save.
            {
                content: "Save the record",
                trigger: ".o_form_button_save",
            },
            // ── Post-Condition — A new record is created and active.
            {
                content: "Record is saved",
                trigger: ".o_form_view.o_form_readonly",
                run: function () {},
            },
            {
                content: "Name shows the value that was filled in",
                trigger:
                    ".o_form_readonly .o_field_widget[name='name']:contains(TOUR Bank CSV)",
                run: function () {},
            },
        ]
    );
});
