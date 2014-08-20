
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

class MrpRoutingOperation(orm.Model):
    _name = 'mrp.routing.operation'
    _description = 'MRP Routing Operation'

    _columns = {
        'name': fields.char('Name', required=True),
        'code': fields.char('Code'),
    }

class MrpRoutingWorkcenter(orm.Model):
    _inherit = 'mrp.routing.workcenter'

    _columns = {
        'operation_id': fields.many2one('mrp.routing.operation', 'Operation',
                                     required=True),
    }

    def onchange_operation(self, cr, uid, ids, operation_id, context=None):
        values= {}
        operation_obj = self.pool['mrp.routing.operation']
        operation = operation_obj.browse(cr, uid, operation_id, context)
        if operation:
            values = {'name': operation.name}
        return {'value': values}
