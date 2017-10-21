odoo.define('kindERP_events.form_widgets', function (require) {
    "use strict";

    var core = require('web.core');
    var common = require('web.form_common');

    var _t = core._t;
    var QWeb = core.qweb;

    /**
     This widget is intended to be used on stat button boolean fields.
     It is a read-only field that will display a simple string "<label of value>".
     */
    var RegistryFieldBooleanButton = common.AbstractField.extend({
        className: 'o_stat_info',
        init: function () {
            this._super.apply(this, arguments);
            switch (this.options["terminology"]) {
                case "registered":
                    this.string_true = _t("Registered");
                    this.hover_true = _t("Check Out");
                    this.string_false = _t("Not Registered");
                    this.hover_false = _t("Check In");
                    break;
            }
        },
        render_value: function () {
            this._super();
            this.$el.html(QWeb.render("RegistryBooleanButton", {widget: this}));
        },
        is_false: function () {
            return false;
        },
    });


    /**
     * Registry of form fields, called by :js:`instance.web.FormView`.
     *
     * All referenced classes must implement FieldInterface. Those represent the classes whose instances
     * will substitute to the <field> tags as defined in OpenERP's views.
     */
    core.form_widget_registry
        .add('register_boolean_button', RegistryFieldBooleanButton);

    /**
     * Registry of widgets usable in the form view that can substitute to any possible
     * tags defined in OpenERP's form views.
     *
     * Every referenced class should extend FormWidget.
     */
});
