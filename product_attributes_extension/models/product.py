
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
                return super(ProductTemplate, self).create_variant_ids(cr, uid, ids,
                                                                        context=context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if not vals.get('no_variants'):
            self.create_variant_ids(cr, uid, ids, context=context)
        value_obj = self.pool['product.attribute.value']
        custom_values = ('attribute_line_ids' in vals or []) and [i for i in vals['attribute_line_ids'] if isinstance(i[2], dict) and 'custom_value'in i[2]]
        for value in custom_values:
            line=self.pool['product.attribute.line'].browse(cr, uid, value[1], context=context)
            range_id = (value_obj.search(
                cr, uid, [('min_range', '<=', float(value[2]['custom_value'])),
                          ('max_range', '>=', float(value[2]['custom_value'])),
                          ('attribute_id', '=', line.attribute_id.id)], context=context))
            if not range_id:
                # TODO create value with min and max
                # equal custom_value or raise error
                raise orm.except_orm(_('Warning'), _('Custom value is not in any range of attribute values'))
            if 'value_ids' in value[2]:
                value[2]['value_ids'][0][2].extend(range_id)
                value[2].pop('custom_value')
            else:
                value[2].pop('custom_value')
                value[2].update({'value_ids': [(6, False, range_id)]})
        return super(ProductTemplate, self).write(cr, uid, ids, vals, context=context)

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
        'attr_line_ids': fields.function(_get_line_ids, type='char', method=True, string="Line Ids"),
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
    _columns ={
               'type': fields.selection([('radio', 'Radio'),
                                  ('select', 'Select'),
                                  ('color', 'Color'),
                                  ('hidden', 'Hidden'),
                                  ('custom', 'Custom')],
                                 string="Type", type="char"),
               }


class ProductAttributeLine(orm.Model):
    _inherit = "product.attribute.line"
    _columns = {
        'obligatory': fields.boolean('Obligatory'),
        'default': fields.many2one('product.attribute.value', 'Default'),
        'attr_type': fields.related('attribute_id', 'type', type='char',
                                    string='Type', store=False),
        'custom_value': fields.char('Custom Value', size=18)}

    def button_assign_value(self, cr, uid, ids, context=None):
        line=self.browse(cr, uid, ids[0], context=context)
        custom_value = float(line.custom_value)
        value_obj = self.pool['product.attribute.value']
        range_ids=[]
        range_id = (value_obj.search(
            cr, uid, [('min_range', '<=', float(custom_value)),
                      ('max_range', '>=', float(custom_value))], context=context))
        for value in value_obj.browse(cr, uid, range_id, context=context):
            if value.min_range != value.max_range:
                range_ids.append(value.id)
        if not range_id:
            # TODO create value with min and max
            # equal custom_value or raise error
            raise orm.except_orm(_('Warning'), _('custom value is not in any range of attribute values'))
        #self.write(cr, uid, ids, {'value_ids': [(4, range_id[0])], 'custom_value': 0}, context=context)
        self.pool['product.template'].write(cr, uid, line.product_tmpl_id.id,
                                            {'attribute_line_ids':[(1, ids[0], {'value_ids': [(4, range_id[0])], 'custom_value': ''})]},
                   context=context)
        return True

    def onchange_assign_value(self, cr, uid, ids, custom_value,
                              context=None):
        range_id = (self.pool['product.attribute.value'].search(
            cr, uid, [('min_range', '>=', float(custom_value)),
                      ('max_range', '<=', float(custom_value))], context=context))
        if not range_id:
            # TODO create value with min and max
            # equal custom_value or raise error
            return {'value': {'custom_value': 'error'}}
#            self.write(cr, uid, ids, {'value_ids': [4, range_id, False]},
#                       context=context)
        return {'value': {'custom_value': '', 'value_ids': [6,0,range_id]}}

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
        'min_range': fields.float('Min', digits=(12, 6)),
        'max_range': fields.float('Max', digits=(12, 6))
        }
