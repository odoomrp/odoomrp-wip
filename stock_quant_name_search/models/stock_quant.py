# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if not args:
            args = []
        if not name:
            return super(StockQuant, self).name_search(
                name=name, args=args, operator=operator, limit=limit)
        quants = self
        product_obj = self.env['product.product']
        product_search = product_obj.name_search(
            name=name, args=None, operator=operator, limit=limit)
        uom_search = self.env['product.uom'].name_search(
            name=name, args=None, operator=operator, limit=limit)
        product_uoms = map(lambda x: x[0], uom_search)
        product_uom_ids = product_obj.search([('uom_id', 'in', product_uoms)])
        product_ids = map(lambda x: x[0], product_search) + product_uom_ids.ids
        quants |= self.search([('product_id', 'in', product_ids)] + args)
        lot_search = self.env['stock.production.lot'].name_search(
            name=name, args=None, operator=operator, limit=limit)
        lot_ids = map(lambda x: x[0], lot_search)
        quants |= self.search([('lot_id', 'in', lot_ids)] + args)
        result = quants.name_get()
        return result
