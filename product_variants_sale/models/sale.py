
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


class SaleOrder(orm.Model):

    _inherit = 'sale.order'
    _columns = {
        'sale_variant_lines': fields.one2many('sale.variant.lines', 'sale_id',
                                              'Sale Variant Lines'),
        }


class AttributeValueLines(orm.Model):
    _name = 'attribute.value.lines'
    _columns = {
        'attribute_id': fields.many2one('product.attribute', 'Attribute'),
        'value_id': fields.many2one('product.attribute.value', 'Value'),
        'sale_variant_line_id': fields.many2one('sale.variant.lines'),
        'custom_value': fields.char('Custom Value', size=18)
        }


class SaleVariantLines(orm.Model):
    _name = 'sale.variant.lines'
    _columns = {
        'sale_id': fields.many2one('sale.order', 'Order'),
        'tmpl_id': fields.many2one('product.template', 'Template'),
        'attribute_lines': fields.one2many(
            'attribute.value.lines', 'sale_variant_line_id', 'Attributes'),
        'final_value_lines': fields.one2many('final.values',
                                             'sale_variant_line_id', 'Values'),
        }

    def _create_variants(self, cr, uid, ids, context=None):
        product_obj = self.pool["product.product"]
        tmpl_obj = self.pool['product.template']
        ctx = context and context.copy() or {}
        if ctx.get("create_product_variant"):
            return None
        ctx.update(active_test=False, create_product_variant=True)
        all_variants = []
        var_qty = []
        sale_variant = self.browse(cr, uid, ids, context=ctx)
        tmpl_id = sale_variant.tmpl_id
        static_values = [attr_line.value_id and attr_line.value_id.id or False
                         for attr_line in sale_variant.attribute_lines]
        attr_line_ids = map(int, tmpl_id.attribute_line_ids)
        final_index = attr_line_ids.index(tmpl_id.final.id)
        for final_line in sale_variant.final_value_lines:
            if final_line.qty:
                final_values = list(static_values)
                final_values.insert(final_index, final_line.value_id.id)
                all_variants.append(filter(lambda x: x, final_values))
                var_qty.append(final_line.qty)
        # check product
        variant_ids_to_active = []
        variants_active_ids = []
        for product_id in tmpl_id.product_variant_ids:
            variants = map(int, product_id.attribute_value_ids)
            if variants in all_variants:
                qty = var_qty[all_variants.index(variants)]
                variants_active_ids.append((product_id.id, qty))
                var_index = all_variants.index(variants)
                all_variants.pop(var_index)
                var_qty.pop(var_index)
                if not product_id.active:
                    variant_ids_to_active.append(product_id.id)
        if variant_ids_to_active:
            product_obj.write(cr, uid, variant_ids_to_active, {'active': True},
                              context=ctx)
        # create new product
        for ind, variant_ids in enumerate(all_variants):
            values = {
                'product_tmpl_id': tmpl_id.id,
                'attribute_value_ids': [(6, 0, variant_ids)]
            }
            id = product_obj.create(cr, uid, values, context=ctx)
            variants_active_ids.append((id, var_qty[ind]))
        return variants_active_ids

    def create_lines(self, cr, uid, ids, context=None):
        sale_obj = self.pool['sale.order']
        sale_line_obj = self.pool['sale.order.line']
        for line in self.browse(cr, uid, ids, context=context):
            product_ids = self._create_variants(cr, uid, ids, context=context)
            for product_id, product_qty in product_ids:
                # product_id_change()??
                order = sale_obj.read(
                    cr, uid, line.sale_id.id,
                    ['pricelist_id', 'partner_id',
                     'date_order', 'fiscal_position'],
                    context=context)
                values = sale_line_obj.product_id_change(
                    cr, uid, [], order['pricelist_id'][0], product_id,
                    qty=product_qty,
                    partner_id=order['partner_id'][0],
                    date_order=order['date_order'],
                    fiscal_position=order['fiscal_position'][0]
                    if order['fiscal_position']
                    else False,
                    flag=False,  # Force name update
                    context=context
                    )
                values['value'].update({
                    'order_id': line.sale_id.id,
                    'product_id': product_id,
                    'product_uom_qty': product_qty})
                sale_line_obj.create(cr, uid, values['value'], context=context)
        return True

    def bring_tmpl_attributes(self, cr, uid, ids, context=None):
        tmpl_obj = self.pool['product.template']
        attribute_ids = []
        value_ids = []
        sale_variant = self.browse(cr, uid, ids, context=context)
        tmpl = tmpl_obj.browse(cr, uid, sale_variant.tmpl_id.id,
                               context=context)
        for line in tmpl.attribute_line_ids:
            if line.id != tmpl.final.id:
                attribute_ids.append((0, 0,
                                      {'attribute_id': line.attribute_id.id}))
            else:
                value_ids = map(lambda x: (0, 0, {'value_id': int(x)}),
                                line.value_ids)
        self.write(cr, uid, ids, {'attribute_lines': attribute_ids,
                                  'final_value_lines': value_ids},
                   context=context)
        return True


class FinalValues(orm.Model):
    _name = 'final.values'
    _columns = {
        'sale_variant_line_id': fields.many2one('sale.variant.lines'),
        'value_id': fields.many2one('product.attribute.value', 'Value'),
        'qty': fields.float('QTY', digits=(12, 6)),
        }
