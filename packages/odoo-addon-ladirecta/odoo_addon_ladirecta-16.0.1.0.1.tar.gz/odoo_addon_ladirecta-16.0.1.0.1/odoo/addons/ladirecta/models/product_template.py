from odoo import fields, models


class ProductProduct(models.Model):

    _inherit = "product.template"

    to_be_printed = fields.Boolean(
        string="To be printed",
    )
