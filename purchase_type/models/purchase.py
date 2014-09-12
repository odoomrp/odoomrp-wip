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
from openerp.osv import orm, fields
from openerp.tools.translate import _


class PurchaseType(orm.Model):
    _name = 'purchase.type'
    _auto = True
    _columns = {
        'name': fields.char('Type', size=128, required=True),
        'sequence': fields.many2one('ir.sequence', 'Sequence', required=True),
    }


class PurchaseOrder(orm.Model):
    _inherit = 'purchase.order'

    def _delete_constraint(self, cr, uid):
        # cr.execute( """ALTER TABLE purchase_order DROP CONSTRAINT
        # purchase_order_name_uniq""")
        return True

    _columns = {
        'type': fields.many2one('purchase.type', 'Type', required=True),
    }
    _defaults = {'name': lambda *a: 'PO/'
                 }

    def create(self, cr, uid, vals, context=None):
        sequence_obj = self.pool['ir.sequence']
        ptype_obj = self.pool['purchase.type']
        if 'type' not in vals:
            condition = [('code', '=', 'purchase.order')]
            sequence_ids = sequence_obj.search(cr, uid, condition,
                                               context=context, limit=1)
            if not sequence_ids:
                raise orm.except_orm(_('Purchase Order Creation Error'),
                                     _('Purchase Order sequence not found'))
            sequence = sequence_obj.browse(cr, uid, sequence_ids[0],
                                           context=context)
            condition = [('sequence', '=', sequence.id)]
            ptype_ids = ptype_obj.search(cr, uid, condition, context=context,
                                         limit=1)
            if not ptype_ids:
                raise orm.except_orm(_('Purchase Order Creation Error'),
                                     _('Purchase Type not found'))
            seq = sequence_obj.get(cr, uid, sequence.code, context=context)
            vals.update({'name': seq,
                         'type': ptype_ids[0]})
        return super(PurchaseOrder, self).create(cr, uid, vals,
                                                 context=context)

    def select_type(self, cr, uid, ids, context=None):
        type_obj = self.pool['purchase.type']
        sequence_obj = self.pool['ir.sequence']
        vals = {}
        for record in self.browse(cr, uid, ids, context):
            if record.type and not record.name:
                type_o = type_obj.browse(cr, uid, record.type.id, context)
                code = type_o.sequence.code
                seq = sequence_obj.get(cr, uid, code, context=context)
                vals.update({'name': seq})
                self.write(cr, uid, [record.id], vals, context=context)
        return ids

    def wkf_confirm_order(self, cr, uid, ids, context=None):
        res = super(PurchaseOrder, self).wkf_confirm_order(cr, uid, ids,
                                                           context)
        self.select_type(cr, uid, ids, context)
        return res

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'state': 'draft',
            'shipped': False,
            'invoiced': False,
            'invoice_ids': [],
            'picking_ids': [],
            'name': 'PO/',
        })
        res = super(orm.Model, self).copy(cr, uid, id, default, context)
        return res
