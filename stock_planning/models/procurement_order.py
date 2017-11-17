# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models


class ProcurementOrder(models.Model):

    _inherit = 'procurement.order'

    def _find_procurements_from_stock_planning(
        self, company, to_date, states=None, from_date=None, category=None,
        template=None, product=None, location_id=None, periods=False,
            without_purchases=False):
        cond = [('company_id', '=', company.id),
                ('date_planned', '<=', to_date)]
        if states:
            cond.append(('state', 'in', states))
        else:
            cond.append(('state', 'not in', ('cancel', 'done')))
        if from_date:
            cond.append(('date_planned', '=>', from_date))
        if product:
            cond.append(('product_id', '=', product.id))
        if location_id:
            cond.append(('location_id', '=', location_id.id))
        procurements = self.search(cond)
        procurements = procurements.filtered(
            lambda x: x.location_id.usage == 'internal')
        if category:
            procurements = procurements.filtered(
                lambda x: x.product_id.product_tmpl_id.categ_id.id ==
                category.id)
        if template:
            procurements = procurements.filtered(
                lambda x: x.product_id.product_tmpl_id.id ==
                template.id)
        if periods:
            return procurements
        if without_purchases:
            procs = self.env['procurement.order']
            for procurement in procurements:
                if not procurement.purchase_id:
                    procs |= procurement
            return procs
        return procurements
