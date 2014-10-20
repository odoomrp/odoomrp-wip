
# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp.osv import orm, fields
from datetime import datetime
from dateutil.relativedelta import relativedelta


class StockProductionLot(orm.Model):
    _inherit = "stock.production.lot"
    _columns = {
        "warrant_limit": fields.datetime("Warranty")
        }

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('product_id'):
            product = self.pool["product.product"].browse(
                cr, uid, vals["product_id"], context=context)
            create_date = ('create_date' in vals and
                           vals['create_date'] or datetime.now())
            if 'sup_warrant' not in context:
                warrant_limit = (
                    product.warranty and
                    (create_date +
                     relativedelta(months=int(product.warranty))))
            else:
                warrant_limit = (
                    create_date +
                    relativedelta(months=int(context['sup_warrant']) +
                                  relativedelta(
                        days=int(31*(context['sup_warrant'] -
                                     int(context['sup_warrant']))))))
            if warrant_limit:
                vals.update({'warrant_limit': warrant_limit})
        return super(StockProductionLot, self).create(cr, uid, vals,
                                                      context=context)


class StockPackOperation(orm.Model):

    _inherit = "stock.pack.operation"

    def create_and_assign_lot(self, cr, uid, id, name, context=None):
        if context is None:
            context = {}
        pack_oper = self.browse(cr, uid, id, context=context)
        if pack_oper.picking_id.location_id.usage == 'supplier':
            sup_obj = self.pool['product.supplierinfo']
            suppinfo_id = sup_obj.search(
                cr, uid, [('name', '=', pack_oper.picking_id.partner_id.id),
                          ('product_tmpl_id', '=',
                           pack_oper.product_id.product_tmpl_id.id)],
                context=context)
            sup = sup_obj.browse(cr, uid, suppinfo_id, context=context)
            sup_warrant = sup and sup[0].warrant_months
            ctx = context.copy()
            ctx.update({'sup_warrant': sup_warrant})
        return super(StockPackOperation, self).create_and_assign_lot(
            cr, uid, id, name, context=ctx)
