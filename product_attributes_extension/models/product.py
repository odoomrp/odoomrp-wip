
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2008-2013 AvanzOSC S.L. (Mikel Arregi) All Rights Reserved
#
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

class ProductCategory(orm.Model):
    _inherit = "product.category"
    _columns = {
        'no_variants': fields.boolean('Sale Time Variants',
                                      help=("Create variants in the"
                                            "time of sale"))}


class ProductTemplate(orm.Model):
    _inherit = "product.template"
    
    def create_variant_ids(self, cr, uid, ids, context=None):
        for tmpl in self.browse(cr, uid, ids, context=context):
            if tmpl.no_variants or tmpl.categ_id.no_variants:
                return True
            else:
                return super(ProductTemplate, self).create_variant_ids(
                    cr, uid, ids, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if not vals.get('no_variants'):
            self.create_variant_ids(cr, uid, ids, context=context)
        return super(ProductTemplate, self).write(cr, uid, ids, vals,
                                                  context=context)

    def _get_line_ids(self, cr, uid, ids, fields, arg, context=None):
        res={}
        line_ids=[]
        for tmpl in self.browse(cr, uid, ids, context=context):
            for line in tmpl.attribute_line_ids:
                line_ids.append(line.id)
            res.update({tmpl.id: line_ids})
        return res

    _columns = {
        'no_variants': fields.boolean('Sale Time Variants',
                                      help=("Create variants in the"
                                            "time of sale")),
        'attr_line_ids': fields.function(_get_line_ids, type='char',
                                         method=True, string="Line Ids"),
        'final': fields.many2one('product.attribute.line', 'Final')}

    def _final_attribute(self,cr, uid, ids, context=None):
        if not isinstance(ids, 'list'):
            ids = [ids]
        for tmpl in self.browse(cr, uid, ids, context=context):
            attrs= [attr.id for attr in tmpl.attribute_line_ids]
            if tmpl.final.id not in attrs:
                return False
        return True

    _constrait = [(_final_attribute, 'This value is not in template values',
                   ['final'])]


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
            ('custom', 'Custom')],
        string="Type", type="char")}


class ProductAttributeLine(orm.Model):
    _inherit = "product.attribute.line"
    _columns = {
        'obligatory': fields.boolean('Obligatory'),
        'default': fields.many2one('product.attribute.value', 'Default'),
        'attr_type': fields.related('attribute_id', 'type', type='char',
                                    string='Type', store=False)}

    def _in_values(self, cr, uid, ids, context=None):
        if not isinstance(ids, 'list'):
            ids = [ids]
        for line in self.browse(cr, uid, ids, context=context):
            values = [value.id for value in line.value_ids]
            if line.default.id in values:
                return False
        return True

    _constrait = [(_in_values, 'This value is not in template values',
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
