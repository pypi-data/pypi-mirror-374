from odoo import fields, models


class CorreosShipmentCode(models.Model):

    _name = "correos.shipment.code"
    _description = "Correos Shipment Code"

    code = fields.Char()

    _sql_constraints = [
        (
            "code_uniq",
            "UNIQUE(code)",
            "Code must be unique!",
        ),
    ]

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.code))
        return result
