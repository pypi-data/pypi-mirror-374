from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    keycloak_connector_enabled = fields.Boolean(string="Keycloak Connector Enables")
    keycloak_url = fields.Char(string="Keycloak URL")
    keycloak_admin_user = fields.Char(string="Keycloak Admin User")
    keycloak_admin_password = fields.Char(string="Keycloak Admin Password")
    keycloak_user_realm_name = fields.Char(string="Keycloak User Realm Name")
    keycloak_realm_name = fields.Char(string="Keycloak Realm Name")
    keycloak_client_id = fields.Char(string="Keycloak Client ID")
    keycloak_client_secret_master_realm = fields.Char(
        string="Keycloak Client Secret Master Realm"
    )
    keycloak_subs_group_id = fields.Char(string="Keycloak Subs Group ID")
