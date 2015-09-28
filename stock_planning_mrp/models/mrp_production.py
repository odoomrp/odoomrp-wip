# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models


class MrpProduction(models.Model):

    _inherit = 'mrp.production'

    def _find_productions_from_stock_planning(
            self, company, to_date, product, warehouse, location,
            from_date=None):
        warehouse_obj = self.env['stock.warehouse']
        cond = [('company_id', '=', company.id),
                ('product_id', '=', product.id),
                ('date_planned', '<=', to_date),
                ('location_dest_id', '=', location.id),
                ('state', 'in', ('draft', 'confirmed', 'ready'))]
        if from_date:
            cond.append(('date_planned', '=>', from_date))
        productions = self.search(cond)
        if not warehouse:
            return productions
        lines = self.env['mrp.production']
        for production in productions:
            cond = [('company_id', '=', company.id),
                    ('lot_stock_id', '=', production.location_dest_id.id)]
            ware = warehouse_obj.search(cond, limit=1)
            if warehouse == ware:
                lines |= production
        return lines
