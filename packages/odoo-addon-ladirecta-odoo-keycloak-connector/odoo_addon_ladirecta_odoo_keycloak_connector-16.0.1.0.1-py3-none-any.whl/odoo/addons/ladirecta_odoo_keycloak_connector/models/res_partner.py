from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    keycloak_user_id = fields.Char(string="Keycloak User ID")
