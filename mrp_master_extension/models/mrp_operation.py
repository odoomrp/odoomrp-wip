
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


class MrpOperation(orm.Model):
    _inherit = 'mrp_operations.operation'
    _name = 'mrp.operation'
    _description = 'MRP Operation'

    _columns = {
        'active': fields.boolean(
            'Active', help="If the active field is set to False, it will allow"
            " you to hide the resource record without removing it."),
        'workcenter_id': fields.many2one('mrp.workcenter', 'Work Center',
                                        required=False),
        'workcenter_ids': fields.many2many(
            'mrp.workcenter', 'mrp_operations_workcenter', 'operation_id',
            'workcenter_id', 'Work centers'),
        'name': fields.char('Name', size=64, required=True),
        'description': fields.text('Description',
                                   help="Description of the operation"),
        'type': fields.selection([('mfo', 'Manufacturing Operation'),
                                  ('mto', 'Maintenance Operation')],
                                 'Operation type', size=64, required=True),
        # Dependecy to work_orders
        # 'operation_line_ids': fields.one2many('mrp.production.workcenter.line',
        #                                      'operation_id', 'Operations'),
        # Dependecy mrp.bom.operations.product
        # 'operations_product': fields.one2many('mrp.bom.operations.product',
        #                                      'operation_id', 'Operations'),
    }

    def create(self, cr, uid, vals, context=None):
        if 'workcenter_ids' in vals:
            if vals['workcenter_ids'][0][2] != []:
                vals['workcenter_id'] = vals['workcenter_ids'][0][2][0]
            else:
                raise orm.except_orm(_('Error!'),
                                     _('One Workcenter must be defined at least'))
        super(MrpOperation, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if 'workcenter_ids' in vals:
            if vals['workcenter_ids'][0][2] != []:
                vals['workcenter_id'] = vals['workcenter_ids'][0][2][0]
        super(MrpOperation, self).write(cr, uid, ids, vals, context=context)

    _defaults = {
        'type': lambda *a: 'mfo',
        'active': lambda *a: True,
    }
