# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
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


class ProductTemplate(orm.Model):
    _inherit = "product.template"

    _columns = {
        'final': fields.many2one('product.attribute.line', 'Final',
                                 domain="[('product_tmpl_id', '=', id)]")
    }

    def _final_attribute(self, cr, uid, ids, context=None):
        if not isinstance(ids, 'list'):
            ids = [ids]
        for tmpl in self.browse(cr, uid, ids, context=context):
            attrs = [attr.id for attr in tmpl.attribute_line_ids]
            if tmpl.final.id not in attrs:
                return False
        return True

    _constraint = [(_final_attribute,
                    _('This value is not in template values'), ['final'])]


class ProductAttribute(orm.Model):
    _inherit = "product.attribute"

    _columns = {
        'type': fields.selection([
            ('radio', 'Radio'),
            ('select', 'Select'),
            ('color', 'Color'),
            ('hidden', 'Hidden'),
            ('range', 'Range'),
            ('dimensions', 'Dimensions'),
            ('custom', 'Custom')], string="Type", type="char"),
    }


class ProductAttributeLine(orm.Model):
    _inherit = "product.attribute.line"

    _columns = {
        'obligatory': fields.boolean('Obligatory'),
        'default': fields.many2one('product.attribute.value', 'Default'),
        'attr_type': fields.related('attribute_id', 'type', type='char',
                                    string='Type', store=False),
    }

    def _check_values(self, cr, uid, ids, context=None):
        if not isinstance(ids, 'list'):
            ids = [ids]
        for line in self.browse(cr, uid, ids, context=context):
            values = [value.id for value in line.value_ids]
            if line.default.id in values:
                return False
        return True

    _constraint = [(_check_values, _('This value is not in template values'),
                   ['final'])]


class ProductAttributeValue(orm.Model):
    _inherit = "product.attribute.value"

    _columns = {
        'custom_value': fields.char('Custom Value', size=128),
        'min_range': fields.float('Min', digits=(12, 6)),
        'max_range': fields.float('Max', digits=(12, 6)),
        'height': fields.float('Height', digits=(12, 6)),
        'width': fields.float('Width', digits=(12, 6)),
        'depth': fields.float('Depth', digits=(12, 6)),
    }
