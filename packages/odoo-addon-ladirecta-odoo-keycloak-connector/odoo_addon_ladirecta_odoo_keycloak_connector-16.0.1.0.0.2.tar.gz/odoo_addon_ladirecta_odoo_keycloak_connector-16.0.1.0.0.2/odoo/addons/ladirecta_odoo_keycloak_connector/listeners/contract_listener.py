from odoo.addons.component.core import Component


class ContractListener(Component):
    _name = "contract.listener"
    _inherit = "base.event.listener"
    _apply_on = ["contract.contract"]

    def on_record_create(self, record, fields=None):
        record.with_delay().create_keycloak_user()
