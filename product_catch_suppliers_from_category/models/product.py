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


class ProductCategory(orm.Model):
    _inherit = 'product.category'

    _columns = {
        'suppliers_ids':
            fields.many2many('res.partner', 'category_supplier_rel',
                             'category_id', 'supplier_id', 'Suppliers'),
    }


class ProductProduct(orm.Model):
    _inherit = 'product.product'

    def onchange_categ_id(self, cr, uid, ids, categ_id, context=None):
        category_obj = self.pool['product.category']
        res = {}
        if categ_id:
            category = category_obj.browse(cr, uid, categ_id, context=context)
            if category.suppliers_ids:
                table = []
                sequence = 0
                for supplier in category.suppliers_ids:
                    sequence += 1
                    vals = {'name': supplier.id,
                            'sequence': sequence,
                            'delay': 1,
                            'min_qty': 1,
                            }
                    table.append((0, 0, vals))
                res = {'seller_ids': table}
        return {'value': res}
