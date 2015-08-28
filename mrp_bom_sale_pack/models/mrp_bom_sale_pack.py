# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api


class MrpBomSaleOrder(models.Model):
    _name = 'mrp.bom.sale.order'

    product_id = fields.Many2one(comodel_name='product.product',
                                 string='Product')
    product_uom = fields.Many2one(comodel_name='product.uom',
                                  string='Unit of Measure ')
    product_uom_qty = fields.Float(string='Quantity (UoS)')
    sale_orders = fields.Many2one(string='Sale order',
                                  comodel_name='sale.order.line')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    mrp_boms = fields.One2many(comodel_name='mrp.bom.sale.order',
                               inverse_name='sale_orders', string='Mrp BoM')
    virtual_stock = fields.Integer(string='Virtual stock')

    @api.multi
    @api.onchange('product_template')
    def onchange_product_template(self):
        super(SaleOrderLine, self).onchange_product_template()
        self.ensure_one()
        mrp_bom_obj = self.env['mrp.bom']
        mrp_bom = []
        stock = []
        if self.product_template:
            mrp_bom = mrp_bom_obj.search([
                ('product_tmpl_id', '=', self.product_template.id),
                ('type', '=', 'phantom')])
            order_lines = []
            for line_ids in mrp_bom.bom_line_ids:
                order_line = {
                    'product_id': line_ids.product_id.id,
                    'product_uom': line_ids.product_uom.id,
                    'product_uom_qty':
                    line_ids.product_qty * self.product_uom_qty,
                }
                stock.append(line_ids.product_id.virtual_available -
                            (line_ids.product_qty))
                order_lines.append(order_line)
            self.mrp_boms = ([(0, 0, oline) for oline in order_lines])
            if stock:
                self.virtual_stock = min(stock)

    @api.multi
    def product_id_change_with_wh_with_bom(
            self, pricelist, product, qty=0, uom=False, qty_uos=0,
            uos=False, name='', partner_id=False, lang=False, update_tax=True,
            date_order=False, packaging=False, fiscal_position=False,
            flag=False, warehouse_id=False, mrp_boms=False,
            virtual_stock=False):
        res = super(SaleOrderLine, self).product_id_change_with_wh(
            pricelist, product, qty=qty, uom=uom, qty_uos=qty_uos, uos=uos,
            name=name, partner_id=partner_id, lang=lang, update_tax=update_tax,
            date_order=date_order, packaging=packaging,
            fiscal_position=fiscal_position, flag=flag,
            warehouse_id=warehouse_id)
        stock = []
        product_obj = self.env['product.product']
        products = []
        for line in mrp_boms:
            if line and line[2] and isinstance(line[2], dict):
                line[2]['product_uom_qty'] = (
                    line[2].get('product_uom_qty', 0) * qty)
                products = product_obj.search(
                    [('id', '=', line[2].get('product_id'))])
                stock.append(
                    products.virtual_available - line[2]['product_uom_qty'])
        if stock:
            res['value'].update({'virtual_stock': min(stock)})
        res['value'].update({'mrp_boms': mrp_boms})
        return res

    @api.model
    def create(self, values):
        if values.get('mrp_boms'):
            mrp_boms = values.get('mrp_boms')
            sale_order = self.env['sale.order']
            sale = sale_order.search([('id', '=', values.get('order_id'))])
            product_obj = self.env['product.product']
            product = product_obj.search([('id', '=',
                                           values.get('product_id'))])
            sale.note = (sale.note or '') + values.get('name') + ' ' + (
                (product.default_code or '') + '\n')
            virtual_stock = values.get('virtual_stock')
            for line in mrp_boms:
                if line and line[2] and isinstance(line[2], dict):
                    values = {
                        'product_id': line[2].get('product_id'),
                        'product_uom': line[2].get('product_uom', False),
                        'product_uom_qty': line[2].get(
                            'product_uom_qty', False),
                        'product_uos_qty': line[2].get(
                            'product_uos_qty', False),
                        'virtual_stock': virtual_stock,
                        'product_uos': line[2].get('product_uos', False),
                        'order_id': values.get('order_id'),
                        'pricelist_id': values.get('pricelist_id'),
                        'partner_id': values.get('partner_id'),
                        'date_order': values.get('date_order'),
                        'fiscal_position': values.get('fisca_position')
                        }
                    res = super(SaleOrderLine, self).create(values)
        return res
