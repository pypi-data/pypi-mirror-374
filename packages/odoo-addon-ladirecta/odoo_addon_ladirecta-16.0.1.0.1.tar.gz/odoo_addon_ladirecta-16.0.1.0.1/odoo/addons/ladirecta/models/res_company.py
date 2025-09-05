from odoo import fields, models


class Company(models.Model):

    _inherit = "res.company"

    correos_image = fields.Image(
        string="Correos Stamp",
        help="Imagen del sello de correos",
        attachment=True,
    )
