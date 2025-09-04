from odoo import models

from ..services.keycloak import KeycloakService


class ContractContract(models.Model):
    _inherit = "contract.contract"

    def create_keycloak_user(self):
        self.ensure_one()

        keycloak = KeycloakService(self.company_id)
        keycloak.create_keycloak_user(self.partner_id)
