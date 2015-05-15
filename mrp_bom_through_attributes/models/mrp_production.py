# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import api, models, fields


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def get_new_components_info(self, product_id, loc_id, loc_dest_id,
                                uom_id, uos_id, qty, workorder):
        move_obj = self.env['stock.move']
        ul_move = move_obj.onchange_product_id(
            prod_id=product_id,
            loc_id=loc_id,
            loc_dest_id=loc_dest_id)
        ul_move['value'].update({
            'product_id': product_id,
            'product_uom': uom_id,
            'product_uos': uos_id,
            'product_qty': qty,
            'work_order': workorder,
            'product_uos_qty': move_obj.onchange_quantity(
                product_id, qty, uom_id,
                uos_id)['value']['product_uos_qty']})
        return ul_move['value']

    def get_raw_products_data(self):
        res = []
        workorder =\
            self.workcenter_lines and self.workcenter_lines[0].id
        for attr_value in self.product_id.attribute_value_ids.filtered(
                'raw_product'):
            raw_product = attr_value.raw_product
            if raw_product:
                bom_obj = self.env['mrp.bom']
                bom_id = bom_obj.with_context(phantom=True)._bom_find(
                    product_id=raw_product.id)
                qty = self.product_qty * attr_value.raw_qty
                if not bom_id:
                    value = self.get_new_components_info(
                        raw_product.id,
                        raw_product.property_stock_production.id,
                        raw_product.property_stock_inventory.id,
                        raw_product.uom_id.id,
                        raw_product.uos_id.id,
                        qty,
                        workorder)
                    res.append(value)
                else:
                    result, result1 = bom_obj._bom_explode(
                        bom_obj.browse(bom_id), raw_product.id,
                        self.product_qty * attr_value.raw_qty)
                    for line in result:
                        product = self.env['product.product'].browse(
                            line['product_id'])
                        value = self.get_new_components_info(
                            line['product_id'],
                            product.property_stock_production.id,
                            product.property_stock_inventory.id,
                            product.uom_id.id,
                            product.uos_id.id,
                            line['product_qty'] * qty,
                            workorder)
                        res.append(value)
        return res

    @api.one
    def action_compute(self, properties=None):
        result = super(MrpProduction, self).action_compute(
            properties=properties)
        res = self.get_raw_products_data()
        self.write({'product_lines': map(lambda x: (0, 0, x), res)})
        return result

    product_id = fields.Many2one()
    raw_products = fields.One2many('mrp.production.product.line',
                                   'raw_production', string='Raw Products')

    @api.one
    @api.onchange('product_id')
    def onchange_bring_raw_products(self):
        self.raw_products = self.get_raw_products_data()


class MrpProductionProductLine(models.Model):
    _inherit = 'mrp.production.product.line'

    raw_production = fields.Many2one('mrp.production', string='Production')


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    def search(self, cr, uid, args, offset=0, limit=None, order=None,
               context=None, count=False):
        if context and context.get('phantom', False):
            args.append(('type', '=', 'phantom'))
        return super(MrpBom, self).search(
            cr, uid, args, offset=offset, limit=limit, order=order,
            context=context, count=count)
