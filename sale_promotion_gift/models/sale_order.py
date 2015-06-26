# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.one
    @api.depends('order_line', 'order_line.offer_id')
    def _calc_gift_products(self):
        self.gift_products.unlink()
        lines_with_price = self.order_line.filtered(lambda x: x.price_unit > 0)
        self.gift_products = [(
            6, 0, lines_with_price.offer_id.gift_products.mapped('id'))]

    gift_products = fields.Many2many(
        comodel_name='gift.product',
        string='Gift products',
        compute='_calc_gift_products')
    final_gift_products = fields.One2many(
        'sale.final.gift.product', 'sale', string='Final gift products',
        copy=False)

    @api.one
    def action_button_confirm(self):
        sale_line_obj = self.env['sale.order.line']
        for line in self.final_gift_products:
            res = sale_line_obj.product_id_change(
                self.pricelist_id.id, line.product.id,
                partner_id=self.partner_id.id, date_order=self.date_order,
                fiscal_position=self.fiscal_position.id)
            vals = res['value']
            tax = [(6, 0, vals['tax_id'])]
            vals.update({'product_id': line.product.id,
                         'order_id': self.id,
                         'product_attributes': False,
                         'tax_id': tax,
                         'price_unit': 0.0
                         })
            sale_line_obj.create(vals)
        return super(SaleOrder, self).action_button_confirm()

    @api.multi
    def button_dump_final_gift_products(self):
        self.ensure_one()
        self.final_gift_products.unlink()
        for line in self.gift_products:
            vals = self._prepare_final_gift_product_data(self.id, line)
            self.env['sale.final.gift.product'].create(vals)
        return True

    def _prepare_final_gift_product_data(self, sale_id, gift_product):
        vals = {'sale': sale_id,
                'product': gift_product.product.id,
                'quantity': gift_product.quantity
                }
        return vals

    @api.one
    @api.constrains('final_gift_products')
    def check_final_gift_products(self):
        categorys = {}
        for line in self.final_gift_products:
            if line.category not in categorys:
                categorys[line.category] = {'quantity': line.quantity}
            else:
                category = categorys[line.category]
                sum_quantity = category.get('quantity') + line.quantity
                categorys[line.category] = {'quantity': sum_quantity}
        for category in categorys:
            datos_array = categorys[category]
            allowed = sum(
                x.quantity for x in self.gift_products.filtered(
                    lambda x: x.category == category))
            if datos_array['quantity'] > allowed:
                name = category.name
                raise exceptions.Warning(
                    _('Total Quantity %s, in final gift products with'
                      ' category %s, exceeds in gift products of the same'
                      ' category with amount %s') % (
                        str(datos_array['quantity']), name, str(allowed)))


class SaleFinalGiftProduct(models.Model):
    _name = 'sale.final.gift.product'
    _description = 'Sale Final gift product'

    sale = fields.Many2one(
        'sale.order', string='Sale Order', copy=False, ondelete='cascade')
    product = fields.Many2one(
        'product.product', string='Product', required=True)
    category = fields.Many2one(
        'product.category', 'Category', related="product.categ_id",
        store=True, readonly=True)
    quantity = fields.Integer(string='Quantity', required=True)

    @api.one
    @api.onchange('product')
    def onchange_product(self):
        if self.product:
            exist = bool(self.sale.gift_products.filtered(
                lambda x: x.category == self.product.categ_id))
            if not exist:
                raise exceptions.Warning(
                    _('Error!: This product is not in a allowed category.'))
