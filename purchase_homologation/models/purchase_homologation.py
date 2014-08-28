# -*- encoding: utf-8 -*-
##############################################################################
#                                                                            #
#  OpenERP, Open Source Management Solution.                                 #
#                                                                            #
#  @author Carlos Sánchez Cifuentes <csanchez@grupovermon.com>               #
#                                                                            #
#  This program is free software: you can redistribute it and/or modify      #
#  it under the terms of the GNU Affero General Public License as            #
#  published by the Free Software Foundation, either version 3 of the        #
#  License, or (at your option) any later version.                           #
#                                                                            #
#  This program is distributed in the hope that it will be useful,           #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              #
#  GNU Affero General Public License for more details.                       #
#                                                                            #
#  You should have received a copy of the GNU Affero General Public License  #
#  along with this program. If not, see <http://www.gnu.org/licenses/>.      #
#                                                                            #
##############################################################################

from openerp.osv import fields, orm


class PurchaseHomologation(orm.Model):

    _name = 'purchase.homologation'

    _description = 'Homologation for suppliers and categories'

    _columns = {
        'category_id': fields.many2one('product.category', 'Category'),
        'comments': fields.text('Comments'),
        'end_date': fields.datetime('Finishing date'),
        'partner_id': fields.many2one('res.partner',
                                      'Supplier', required=True),
        'product_id': fields.many2one('product.product', 'Product',
                                      domain=[('purchase_ok', '=', True)]),
        'start_date': fields.datetime('Beginning date'),
    }
