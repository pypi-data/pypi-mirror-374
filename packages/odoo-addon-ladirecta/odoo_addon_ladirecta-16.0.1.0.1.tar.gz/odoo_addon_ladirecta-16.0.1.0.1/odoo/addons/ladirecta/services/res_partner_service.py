from marshmallow import fields

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component
from odoo.addons.datamodel.core import Datamodel


class PartnerSubscriptor(Datamodel):
    _name = "partner.subscriptor"

    id = fields.Integer(required=True, allow_none=False)
    name = fields.String(required=True, allow_none=False)
    subscriptor = fields.Boolean(required=True, allow_none=False)


class PartnerSearchParam(Datamodel):
    _name = "partner.search.param"

    id = fields.Integer(required=False, allow_none=False)


class PartnerApiService(Component):
    _inherit = "base.rest.service"
    _name = "res.partner.api.service"
    _usage = "partner"
    _collection = "api_common_base.services"
    _description = """ """

    @restapi.method(
        [(["/<int:_id>/subscriptor"], "GET")],
        output_param=restapi.Datamodel("partner.subscriptor"),
    )
    def search(self, _id):
        PartnerSubscriptor = self.env.datamodels["partner.subscriptor"]
        partner = self.env["res.partner"].browse(_id)
        return PartnerSubscriptor(
            id=partner.id, name=partner.name, subscriptor=partner.has_active_contracts()
        )
