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
            without_purchases=False, without_productions=False):
        procurements = super(
            ProcurementOrder, self)._find_procurements_from_stock_planning(
            company, to_date, states=states, from_date=from_date,
            category=category, template=template, product=product,
            location_id=location_id, periods=periods,
            without_purchases=without_purchases)
        if periods:
            return procurements
        if without_productions:
            procurements = procurements.filtered(lambda x: not x.production_id)
        return procurements
