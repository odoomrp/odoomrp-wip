# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models


class MrpProduction(models.Model):

    _inherit = 'mrp.production'

    def _find_productions_from_stock_planning(
        self, company, to_date, product, location, state=None,
            from_date=None):
        cond = [('company_id', '=', company.id),
                ('product_id', '=', product.id),
                ('date_planned', '<=', to_date),
                ('location_dest_id', '=', location.id),
                ('state', '=', 'draft')]
        if state:
            cond.append(('state', '=', state))
        if from_date:
            cond.append(('date_planned', '=>', from_date))
        productions = self.search(cond)
        return productions
