from werkzeug.exceptions import NotFound

from odoo import _

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest.http import wrapJsonException
from odoo.addons.component.core import Component

from . import schemas


class ResPartnerService(Component):
    _name = "res.partner.rest.service"
    _inherit = "base.rest.service"
    _usage = "partner"
    _collection = "api_common_base.services"
    _description = """ ResPartner API for FemProcomuns """

    @restapi.method(
        [(["/<int:_id>"], "GET")],
        input_param=restapi.CerberusValidator("_validator_get"),
        output_param=restapi.CerberusValidator("_validator_return_get"),
        auth="api_key",
    )
    def get(self, _id):
        partner = self.env["res.partner"].browse(_id)
        if not partner:
            raise wrapJsonException(NotFound(_("No partner for id %s") % _id))
        return self._to_dict(partner)

    def _to_dict(self, partner):
        # Check if partner has contracts active
        has_contracts = self.env["contract.contract"].search(
            [("partner_id", "=", partner.id)]
        )
        return {
            "id": partner.id,
            "name": partner.name,
            "email": partner.email or "",
            "is_subscriber": bool(has_contracts),
        }

    def _validator_get(self):
        return schemas.S_RES_PARTNER_GET

    def _validator_return_get(self):
        return schemas.S_RES_PARTNER_RETURN_GET
