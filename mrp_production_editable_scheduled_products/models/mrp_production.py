# -*- coding: utf-8 -*-
# (c) 2014 Daniel Campos - AvanzOSC
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models


class MrpProductionProductLine(models.Model):
    _inherit = 'mrp.production.product.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom = self.product_id.uom_id.id
            self.name = self.product_id.name
            try:
                self.product_tmpl_id = self.product_id.product_tmpl_id
            except:
                # This is in case mrp_product_variants module is not installed
                pass
