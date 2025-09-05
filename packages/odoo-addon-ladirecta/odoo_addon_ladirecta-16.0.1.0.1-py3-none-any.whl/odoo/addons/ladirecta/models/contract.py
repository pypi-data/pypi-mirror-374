from odoo import fields, models


class Contract(models.Model):

    _inherit = "contract.contract"

    delivery_partner_id = fields.Many2one(
        "res.partner",
        string="Delivery Contact",
    )

    def get_delivery_partner_id(self):
        self.ensure_one()
        return self.delivery_partner_id or self.partner_id
