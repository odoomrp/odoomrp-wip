# -*- coding: utf-8 -*-
# © 2014-2016 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def action_production_end(self):
        self.ensure_one()
        result = super(MrpProduction, self).action_production_end()
        product = self.product_id
        product.last_mrp_id = self.id
        return result
