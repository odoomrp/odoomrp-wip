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
        for attr_value in self.product_id.attribute_value_ids:
            if attr_value.raw_product:
                raw_product = attr_value.raw_product
                value = self.get_new_components_info(
                    raw_product.id,
                    raw_product.property_stock_production.id,
                    raw_product.property_stock_inventory.id,
                    raw_product.uom_id.id,
                    raw_product.uos_id.id,
                    self.product_qty * attr_value.raw_qty,
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
