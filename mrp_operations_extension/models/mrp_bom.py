
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

from openerp.osv import orm, fields
from openerp.tools.translate import _


class MrpBomLine(orm.Model):
    _inherit = 'mrp.bom.line'

    def _get_operation(self, cr, uid, context=None):
        routing_obj = self.pool['mrp.routing.operation']
        ids = routing_obj.search(cr, uid, [], context=context)
        res = routing_obj.read(cr, uid, ids, ['name', 'id'],
                               context=context)
        res = [(r['id'], r['name']) for r in res]
        return res

    _columns = {
        'operation': fields.many2one('mrp.routing.operation', 'Consumed',
                                     selection=_get_operation),
    }
