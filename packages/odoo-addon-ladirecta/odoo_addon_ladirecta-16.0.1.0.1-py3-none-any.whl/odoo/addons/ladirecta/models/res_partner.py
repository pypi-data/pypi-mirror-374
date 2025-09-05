from odoo import fields, models


class Partner(models.Model):

    _inherit = "res.partner"

    correos_code_id = fields.Many2one(
        "correos.shipment.code",
        string="Correos Shipment Code",
    )

    def get_correos_image(self):
        self.ensure_one()
        return self.env.company.correos_image

    def has_active_contracts(self):
        self.ensure_one()
        today = fields.Date.context_today(self)

        active_contracts = self.env["contract.contract"].search(
            [
                "|",
                ("delivery_partner_id", "=", self.id),
                "&",
                ("partner_id", "=", self.id),
                ("delivery_partner_id", "=", False),
                "&",
                ("contract_line_ids.date_start", "<=", today),
                "|",  # Condiciones OR
                ("contract_line_ids.date_end", ">=", today),
                ("contract_line_ids.date_end", "=", False),
            ]
        )
        return bool(active_contracts)

    def has_active_printable_contracts(self):
        self.ensure_one()
        today = fields.Date.context_today(self)

        active_contracts = self.env["contract.contract"].search(
            [
                "&",
                (
                    "contract_line_ids.product_id.to_be_printed",
                    "=",
                    True,
                ),
                "|",
                ("delivery_partner_id", "=", self.id),
                "&",
                ("partner_id", "=", self.id),
                ("delivery_partner_id", "=", False),
                "&",
                ("contract_line_ids.date_start", "<=", today),
                "|",
                ("contract_line_ids.date_end", ">=", today),
                ("contract_line_ids.date_end", "=", False),
            ]
        )

        return bool(active_contracts)
