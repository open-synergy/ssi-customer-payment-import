// Copyright 2026 OpenSynergy Indonesia
// Copyright 2026 PT. Simetri Sinergi Indonesia
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define(
    "ssi_customer_payment_import_operating_unit.customer_payment_import_tour",
    function (require) {
        "use strict";

        var tour = require("web_tour.tour");

        // IK: docs/customer_payment_import/01-create.md (E1 delta --
        // Additional Fields). Navigation (open app -> Account Receivable
        // -> Customer Payment Imports -> New) is taken from the base IK
        // ssi_customer_payment_import/docs/customer_payment_import/01-
        // create.md Flow steps 1-2 -- see skill odoo-development-ui-test,
        // scope-and-boundaries.md §1 ("Backing dua file: tour extension =
        // base IK ∪ delta IK"). The delta assertion comes from this
        // module's own IK: the Operating Unit field is visible on the
        // create form for a user in the
        // operating_unit.group_multi_operating_unit group. The tour stops
        // there; it does not fill, save, or confirm (E1 delta-only).
        tour.register(
            "ssi_customer_payment_import_operating_unit_customer_payment_import_create",
            {
                test: true,
                url: "/web",
            },
            [
                // ── Base Flow 1 — Open the Financial Accounting >
                // Account Receivable > Customer Payment Imports menu.
                tour.stepUtils.showAppsMenuItem(),
                {
                    content: "Open the Financial Accounting app",
                    trigger:
                        '.o_app[data-menu-xmlid="ssi_financial_accounting.menu_root_financial_accounting"]',
                },
                {
                    content: "Open the Account Receivable menu",
                    trigger:
                        '.o_menu_sections [data-menu-xmlid="ssi_financial_accounting.menu_account_receivable"]',
                },
                {
                    content: "Open the Customer Payment Imports menu",
                    trigger:
                        '.o_menu_sections [data-menu-xmlid="ssi_customer_payment_import.customer_payment_import_menu"]',
                },
                {
                    content: "Customer Payment Import list is displayed",
                    trigger:
                        ".o_control_panel .breadcrumb-item.active:contains(Customer Payment Import)",
                    extra_trigger: ".o_list_view",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },

                // ── Base Flow 2 — Click the New button. (14.0: "Create")
                {
                    content: "Click New",
                    trigger: ".o_list_button_add",
                    extra_trigger: ".o_list_view",
                },
                {
                    content: "Form is open in edit mode",
                    trigger: ".o_form_view.o_form_editable",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },

                // ── Delta assertion — the Operating Unit field is
                // visible on the create form for a user in the multi
                // operating unit group. The tour stops here (E1
                // delta-only).
                {
                    content: "Operating Unit field is visible on the form",
                    trigger:
                        ".o_form_view.o_form_editable .o_field_widget[name='operating_unit_id']",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },
            ]
        );
    }
);
