
# -*- encoding: utf-8 -*-
##############################################################################
#
#    Daniel Campos (danielcampos@avanzosc.es) Date: 06/10/2014
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

from openerp import models, fields


class PricelistLine(models.Model):
    _name = 'pricelist.line'
    _description = 'Lineas de Fichero'

    code = fields.Char('Product Code')
    info = fields.Char('Product Description')
    price = fields.Float('Product Price')
    discount_1 = fields.Float('Product Discount 1')
    discount_2 = fields.Float('Product Discount 2')
    retail = fields.Float('Retail Price')
    pdv1 = fields.Float('PDV1')
    pdv2 = fields.Float('PDV2')
    fail = fields.Boolean('Fail')
    fail_reason = fields.Char('Fail Reason')
    file_load = fields.Many2one('file.price.load', 'Load')
