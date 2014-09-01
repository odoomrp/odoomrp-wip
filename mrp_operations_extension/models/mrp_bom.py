
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2008-2014 AvanzOSC (Daniel). All Rights Reserved
#    Date: 10/07/2014
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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

from openerp import models, fields, api


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.model
    def _bom_explode(self, bom, product, factor, properties=None, level=0,
                     routing_id=False, previous_products=None,
                     master_bom=None):
        res = super(MrpBom, self)._bom_explode(bom, product, factor,
                                               properties, level, routing_id,
                                               previous_products, master_bom)
        # process 1 of results
        n = 0
        bom_lines = bom.bom_line_ids
        for data in res[0]:
            if 'product_id' in data:
                for bom_line in bom_lines:
                    if bom_line.product_id.id == data['product_id']:
                        res[0][n].update({'operation': bom_line.operation.id})
            n += 1
        return res


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    def _get_operation(self, cr, uid, context=None):
        routing_obj = self.pool['mrp.routing.operation']
        ids = routing_obj.search(cr, uid, [], context=context)
        res = routing_obj.read(cr, uid, ids, ['name', 'id'],
                               context=context)
        res = [(r['id'], r['name']) for r in res]
        return res

    operation = fields.Many2one('mrp.routing.workcenter', 'Consumed',)
    # domain=[('operation','in','routing_id.workcenter_lines')])
