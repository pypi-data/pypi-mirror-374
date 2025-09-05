from odoo import fields, models


class PrintShipmentTagsWizard(models.TransientModel):
    """
    A transient model for the creation of the tags for
    the shipments. The user can only define the Correos
    Shipment Code to select a subgroup of tags to print.
    """

    _name = "print.shipment.tags.wizard"
    _description = "Print Shipment Tags"

    correos_shipment_code_id = fields.Many2one(
        "correos.shipment.code",
        string="Correos Shipment Code",
        required=True,
    )

    def print_shipment_tags(self):
        self.ensure_one()
        paper_shipments = (
            self.env["contract.line"]
            .search(
                [
                    ("product_id.to_be_printed", "=", True),
                    ("contract_id.date_start", "<=", fields.Date.context_today(self)),
                    "|",
                    ("contract_id.date_end", ">=", fields.Date.context_today(self)),
                    ("contract_id.date_end", "=", False),
                ]
            )
            .filtered(
                lambda x: x.contract_id.get_delivery_partner_id().correos_code_id
                == self.correos_shipment_code_id
            )
        )
        return self.env.ref("ladirecta.report_shipment_tag").report_action(
            paper_shipments
        )
