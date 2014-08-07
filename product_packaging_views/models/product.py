# -*- encoding: utf-8 -*-
##############################################################################
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
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp.osv import orm, fields


class ProductTemplate(orm.Model):
    _inherit = 'product.template'

    _columns = {
        'packaging_ids': fields.one2many('product.packaging',
                                         'product_tmpl_id',
                                         'Packagings'),
    }


class ProductUl(orm.Model):
    _inherit = 'product.ul'

    _columns = {
        'packaging_ids': fields.one2many('product.packaging', 'ul',
                                         'Packagings'),
    }
