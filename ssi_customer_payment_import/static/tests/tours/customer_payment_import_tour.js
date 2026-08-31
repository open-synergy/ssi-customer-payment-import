// Copyright 2026 OpenSynergy Indonesia
// Copyright 2026 PT. Simetri Sinergi Indonesia
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define("ssi_customer_payment_import.customer_payment_import_tour", function (
    require
) {
    "use strict";

    var tour = require("web_tour.tour");

    function openMenu() {
        return [
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
                content: "Customer Payment Imports list is displayed",
                trigger:
                    ".o_control_panel .breadcrumb-item.active:contains(Customer Payment Imports)",
                extra_trigger: ".o_list_view",
                run: function () {
                    // Assertion only.
                },
            },
        ];
    }

    // IK: docs/customer_payment_import/01-create.md
    tour.register(
        "ssi_customer_payment_import_customer_payment_import_create",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // ── Flow 1 — Open the Financial Accounting > Account
            // Receivable > Customer Payment Imports menu.
            openMenu(),
            [
                // ── Flow 2 — Click the New button.
                {
                    content: "Click Create",
                    trigger: ".o_list_button_add",
                    extra_trigger: ".o_list_view",
                },
                {
                    content: "Form is open in edit mode",
                    trigger: ".o_form_view.o_form_editable",
                    run: function () {
                        // Assertion only.
                    },
                },
                // ── Flow 3 — Fill in Type and Journal.
                {
                    content: "Select the Type",
                    trigger: ".o_field_many2one[name='type_id'] input",
                    extra_trigger: ".o_form_view.o_form_editable",
                    run: "text TOUR Bank CSV Type",
                },
                {
                    content: "Pick the Type from the dropdown",
                    trigger:
                        ".ui-autocomplete .ui-menu-item a:contains(TOUR Bank CSV Type)",
                    in_modal: false,
                },
                {
                    content: "Select the Journal",
                    trigger: ".o_field_many2one[name='journal_id'] input",
                    run: "text TOUR Bank Journal",
                },
                {
                    content: "Pick the Journal from the dropdown",
                    trigger:
                        ".ui-autocomplete .ui-menu-item a:contains(TOUR Bank Journal)",
                    in_modal: false,
                },
                // ── Flow 4 — Fill in Account.
                {
                    content: "Select the Account",
                    trigger: ".o_field_many2one[name='account_id'] input",
                    run: "text TOUR Bank Account",
                },
                {
                    content: "Pick the Account from the dropdown",
                    trigger:
                        ".ui-autocomplete .ui-menu-item a:contains(TOUR Bank Account)",
                    in_modal: false,
                },
                // ── Flow 5/6 — Import File is a raw <input type="file">.
                // Attaching a real file to a hidden file input is not
                // reliable across browsers (odoo-development-ui-test,
                // patterns.md §Q), so this tour only verifies the widget
                // and the Load Data button are present -- it does not
                // upload a file or click Load Data. Reading an uploaded
                // file into Import Data lines is covered by the YAML
                // unit test, not by this tour.
                {
                    content: "Import File widget is displayed",
                    trigger: ".o_field_widget[name='import_file']",
                    run: function () {
                        // Assertion only.
                    },
                },
                {
                    content: "Load Data button is visible and enabled",
                    trigger: ".o_form_view button[name='action_load_data']:enabled",
                    run: function () {
                        // Assertion only -- this button mutates the
                        // record (type="object"); it must not be
                        // auto-clicked. See patterns.md §Q.
                    },
                },
                // ── Flow 10 — Click Save.
                {
                    content: "Save the record",
                    trigger: ".o_form_button_save",
                },
                // ── Post-Condition — A new record is created in Draft.
                {
                    content: "Record is saved",
                    trigger: ".o_form_view.o_form_readonly",
                    run: function () {
                        // Assertion only.
                    },
                },
                {
                    content: "Status is Draft",
                    trigger:
                        ".o_statusbar_status .o_arrow_button[data-value='draft'].btn-primary",
                    run: function () {
                        // Assertion only -- do not click the current
                        // state pill.
                    },
                },
            ]
        )
    );

    // IK: docs/customer_payment_import/04-confirm.md
    tour.register(
        "ssi_customer_payment_import_customer_payment_import_confirm",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // ── Flow 1 — Open the menu.
            openMenu(),
            [
                // ── Flow 2 — Open the record to confirm.
                {
                    content: "Open the record",
                    trigger:
                        ".o_data_row:contains(TOUR-CPI-CONFIRM) .o_data_cell:first",
                    extra_trigger: ".o_list_view",
                },
                {
                    content: "Form is displayed",
                    trigger: ".o_form_view",
                    run: function () {
                        // Assertion only.
                    },
                },
                // ── Flow 3 — Click the Confirm button.
                {
                    content: "Click the Confirm button",
                    trigger: ".o_statusbar_buttons button[name='action_confirm']",
                    extra_trigger: ".o_form_view",
                },
                // ── Flow 4 — Click OK on the confirmation dialog.
                {
                    content: "Confirm the dialog",
                    trigger: ".modal-footer button.btn-primary",
                    in_modal: true,
                },
                // ── Post-Condition — Status changes to Waiting for
                // Approval.
                {
                    content: "Status is Waiting for Approval",
                    trigger:
                        ".o_statusbar_status .o_arrow_button[data-value='confirm'].btn-primary",
                    run: function () {
                        // Assertion only -- do not click the current
                        // state pill.
                    },
                },
            ]
        )
    );

    // IK: docs/customer_payment_import/05-approve.md
    tour.register(
        "ssi_customer_payment_import_customer_payment_import_approve",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // ── Flow 1 — Open the menu.
            openMenu(),
            [
                // ── Flow 2 — Open the record to approve.
                {
                    content: "Open the record",
                    trigger:
                        ".o_data_row:contains(TOUR-CPI-APPROVE) .o_data_cell:first",
                    extra_trigger: ".o_list_view",
                },
                {
                    content: "Form is displayed",
                    trigger: ".o_form_view",
                    run: function () {
                        // Assertion only.
                    },
                },
                // ── Flow 3 — Click the Approve button.
                {
                    content: "Click the Approve button",
                    trigger:
                        ".o_statusbar_buttons button[name='action_approve_approval']",
                    extra_trigger: ".o_form_view",
                },
                // ── Flow 4 — Click OK on the confirmation dialog.
                {
                    content: "Confirm the dialog",
                    trigger: ".modal-footer button.btn-primary",
                    in_modal: true,
                },
                // ── Post-Condition — the single approval level is
                // fulfilled, so the import automatically moves past
                // Waiting for Approval (see docs/customer_payment_import
                // /09-auto-done.md for what happens next).
                {
                    content: "Status is no longer Waiting for Approval",
                    trigger:
                        ".o_statusbar_status:not(:has(.o_arrow_button[data-value='confirm'].btn-primary))",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        )
    );

    // IK: docs/customer_payment_import/10-cancel.md
    tour.register(
        "ssi_customer_payment_import_customer_payment_import_cancel",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // ── Flow 1 — Open the menu.
            openMenu(),
            [
                // ── Flow 2 — Open the record to cancel.
                {
                    content: "Open the record",
                    trigger: ".o_data_row:contains(TOUR-CPI-CANCEL) .o_data_cell:first",
                    extra_trigger: ".o_list_view",
                },
                {
                    content: "Form is displayed",
                    trigger: ".o_form_view",
                    run: function () {
                        // Assertion only.
                    },
                },
                // ── Flow 3 — Click the Cancel button.
                {
                    content: "Click the Cancel button",
                    trigger: ".o_statusbar_buttons button:contains(Cancel)",
                    extra_trigger: ".o_form_view",
                },
                // ── Flow 4 — In the wizard, select the Cancellation
                // Reason. `cancel_reason_id` uses widget="radio", not a
                // many2one dropdown -- pick the option by its label.
                {
                    content: "Wizard is open",
                    trigger: ".o_form_view",
                    run: function () {
                        // Assertion only.
                    },
                },
                {
                    content: "Select the cancellation reason",
                    trigger: ".o_radio_item label:contains(TOUR Cancel Reason)",
                },
                // ── Flow 5 — Click Confirm.
                {
                    content: "Confirm the wizard",
                    trigger: ".modal-footer button[name='action_confirm']",
                },
                // ── Flow 6 — Click OK on the confirmation dialog.
                {
                    content: "Confirm the dialog",
                    trigger: ".modal-footer button.btn-primary",
                    in_modal: true,
                },
                // ── Post-Condition — Status changes to Queue Cancel (see
                // docs/customer_payment_import/11-auto-cancel.md for the
                // automatic final step to Cancelled).
                {
                    content: "Status is no longer Draft",
                    trigger:
                        ".o_statusbar_status:not(:has(.o_arrow_button[data-value='draft'].btn-primary))",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        )
    );

    // IK: docs/customer_payment_import/12-restart.md
    tour.register(
        "ssi_customer_payment_import_customer_payment_import_restart",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // ── Flow 1 — Open the menu.
            openMenu(),
            [
                // ── Flow 2 — Open the record to restart.
                {
                    content: "Open the record",
                    trigger:
                        ".o_data_row:contains(TOUR-CPI-RESTART) .o_data_cell:first",
                    extra_trigger: ".o_list_view",
                },
                {
                    content: "Form is displayed",
                    trigger: ".o_form_view",
                    run: function () {
                        // Assertion only.
                    },
                },
                // ── Flow 3 — Click the Restart button.
                {
                    content: "Click the Restart button",
                    trigger: ".o_statusbar_buttons button[name='action_restart']",
                    extra_trigger: ".o_form_view",
                },
                // ── Flow 4 — Click OK on the confirmation dialog.
                {
                    content: "Confirm the dialog",
                    trigger: ".modal-footer button.btn-primary",
                    in_modal: true,
                },
                // ── Post-Condition — Status returns to Draft.
                {
                    content: "Status is Draft",
                    trigger:
                        ".o_statusbar_status .o_arrow_button[data-value='draft'].btn-primary",
                    run: function () {
                        // Assertion only -- do not click the current
                        // state pill.
                    },
                },
            ]
        )
    );
});
