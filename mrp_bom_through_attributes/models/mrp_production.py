# -*- coding: utf-8 -*-
# © 2015 Mikel Arregi <mikelarregi@avanzosc.es>
# © 2015 Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>
# © 2015 Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def get_new_components_info(self, product, qty, workorder):
        move_obj = self.env['stock.move']
        ul_move = move_obj.onchange_product_id(
            prod_id=product.id,
            loc_id=product.property_stock_production.id,
            loc_dest_id=product.property_stock_inventory.id)
        ul_move['value'].update({
            'product_id': product.id,
            'product_uom': product.uom_id.id,
            'product_uos': product.uos_id.id,
            'product_qty': qty,
            'work_order': workorder.id,
            'product_uos_qty': move_obj.onchange_quantity(
                product.id, qty, product.uom_id.id,
                product.uos_id.id)['value']['product_uos_qty']})
        return ul_move['value']

    def get_raw_products_data(self):
        res = []
        workorder = self.workcenter_lines[:1]
        for attr_value in self.product_id.attribute_value_ids.filtered(
                'raw_product'):
            raw_product = attr_value.raw_product
            bom_obj = self.env['mrp.bom']
            bom_id = bom_obj.with_context(phantom=True)._bom_find(
                product_id=raw_product.id)
            qty = self.product_qty * attr_value.raw_qty
            if not bom_id:
                res.append(self.get_new_components_info(
                    raw_product, qty, workorder))
            else:
                bom = bom_obj.browse(bom_id).with_context(production=self)
                result, result1 = bom._bom_explode(
                    raw_product, self.product_qty * attr_value.raw_qty)
                for line in result:
                    product = self.env['product.product'].browse(
                        line['product_id'])
                    res.append(self.get_new_components_info(
                        product, line['product_qty'] * qty, workorder))
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
