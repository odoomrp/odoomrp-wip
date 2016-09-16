# -*- coding: utf-8 -*-
# © 2016 Ainara Galdona <ainaragaldona@avanzosc.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class ChangeProductionQty(models.TransientModel):

    _inherit = 'change.production.qty'

    @api.multi
    def change_prod_qty(self):
        res = super(ChangeProductionQty, self).change_prod_qty()
        record_id = self.env.context.get('active_id', False)
        prod_obj = self.env['mrp.production']
        production = prod_obj.browse(record_id)
        for product_line in production.product_lines:
            move = production.move_lines.filtered(
                lambda x: x.product_id.id == product_line.product_id.id)
            move.write({'product_uom_qty': product_line.product_qty})
        return res
