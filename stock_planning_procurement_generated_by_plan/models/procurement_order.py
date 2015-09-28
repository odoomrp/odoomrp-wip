# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models


class ProcurementOrder(models.Model):

    _inherit = 'procurement.order'

    def _find_procurements_from_stock_planning(
        self, company, to_date, states, from_date=None, category=None,
        template=None, product=None, warehouse=None, location_id=None,
            without_purchases=False, without_productions=False, level=None):
        procurements = super(
            ProcurementOrder, self)._find_procurements_from_stock_planning(
            company, to_date, states, from_date=from_date, category=category,
            template=template, product=product, warehouse=warehouse,
            location_id=location_id, without_purchases=without_purchases)
        if not level:
            return procurements
        procs = self.env['procurement.order']
        for procurement in procurements:
            if ((level == 0 and procurement.level == 0) or
                    (level != 0 and procurement.level >= level)):
                procs |= procurement
        return procs
