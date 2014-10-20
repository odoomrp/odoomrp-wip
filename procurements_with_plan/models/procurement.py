# -*- encoding: utf-8 -*-
##############################################################################
#
#    Avanzosc - Avanced Open Source Consulting
#    Copyright (C) 2011 - 2014 Avanzosc <http://www.avanzosc.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    plan_id = fields.Many2one('procurement.plan', string='Plan')
    origin_state = fields.Selection([('cancel', 'Cancelled'),
                                     ('confirmed', 'Confirmed'),
                                     ('exception', 'Exception'),
                                     ('running', 'Running'),
                                     ('done', 'Done')
                                     ], string='Origin Status')

#    @api.model
#    def _prepare_orderpoint_procurement(self, orderpoint, product_qty):
#        result = super(ProcurementOrder, self)._prepare_orderpoint_procurement(
#            orderpoint, product_qty)
#        if 'plan_id' in self.env.context:
#            result.update({'plan_id': self.env.context.get('plan_id')})
#        return result

    @api.model
    def create(self, data):
        print '*** ESTOY EN CREATE: data: ' + str(data)
        found = False
        if 'plan_id' in self.env.context and not 'plan-id' in data:
            plan_id = self.env.context.get('plan_id')
            found = True
        proc_id = super(ProcurementOrder, self).create(data)
        if found:
            proc = self.browse(proc_id)
            # Descomentar Alfredo
            # proc.write({'plan_id': plan_id})
        return proc_id

    def write(self, cr, uid, ids, vals, context=None):
        purchase_line_obj = self.pool['purchase.order.line']
        purchase_obj = self.pool['purchase.order']
        if 'purchase_line_id' in vals:
            purchase_line_id = vals.get('purchase_line_id')
            if purchase_line_id:
                purchase_line = purchase_line_obj.browse(
                    cr, uid, purchase_line_id, context=context)
                proc = self.browse(cr, uid, ids[0], context=context)
                if purchase_line.order_id and proc.plan_id:
                    my_vals = {'plan_id': proc.plan_id.id}
                    purchase_obj.write(cr, uid, [purchase_line.order_id.id],
                                       my_vals, context=context)
        result = super(ProcurementOrder, self).write(cr,uid, ids, vals,
                                                     context=context)
        return result
