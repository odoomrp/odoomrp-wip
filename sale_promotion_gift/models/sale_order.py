# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.one
    @api.depends('order_line', 'order_line.offer_id')
    def _calc_promotion_gift_products(self):
        self.promotion_gift_products.unlink()
        promotions = []
        for line in self.order_line:
            if line.offer_id and line.offer_id.promotion_gift_products:
                for promotion in line.offer_id.promotion_gift_products:
                    promotions.append(promotion.id)
        self.promotion_gift_products = [(6, 0, promotions)]

    promotion_gift_products = fields.Many2many(
        comodel_name='promotion.gift.product',
        string='Promotion gift products',
        compute='_calc_promotion_gift_products')
    final_gift_products = fields.One2many(
        'sale.final.gift.product', 'sale', string='Final gift products',
        copy=False)

    @api.one
    def action_button_confirm(self):
        sale_line_obj = self.env['sale.order.line']
        if self.final_gift_products:
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
                             'tax_id': tax})
                sale_line_obj.create(vals)
        return super(SaleOrder, self).action_button_confirm()

    @api.multi
    def button_calculate_final_gift_products(self):
        self.ensure_one()
        self.final_gift_products.unlink()
        for line in self.promotion_gift_products:
            vals = {'sale': self.id,
                    'product': line.product.id,
                    'quantity': line.quantity
                    }
            self.env['sale.final.gift.product'].create(vals)
        return True

    @api.one
    @api.constrains('final_gift_products')
    def check_final_gift_products(self):
        if self.final_gift_products:
            categorys = {}
            for line in self.final_gift_products:
                found = False
                for data in categorys:
                    datos_array = categorys[data]
                    category = datos_array['category']
                    quantity = datos_array['quantity']
                    if category.id == line.category.id:
                        found = True
                        quantity += line.quantity
                        categorys[data].update({'quantity': quantity})
                if not found:
                    my_vals = {'category': line.category,
                               'quantity': line.quantity,
                               }
                    categorys[(line.category.id)] = my_vals
            for data in categorys:
                datos_array = categorys[data]
                allowed = sum(
                    x.quantity for x in self.promotion_gift_products.filtered(
                        lambda x: x.category == datos_array['category']))
                if datos_array['quantity'] > allowed:
                    name = datos_array['category'].name
                    raise exceptions.Warning(
                        _('ERROR in Final gift products'),
                        _('Total Quantity %s, in final gift products with'
                          ' category %s, exceeds in Promotion gift products of'
                          ' the same category with amount %s') % (
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
            exist = bool(self.sale.promotion_gift_products.filtered(
                lambda x: x.category == self.product.categ_id))
            if not exist:
                raise exceptions.Warning(
                    _('Error!: This product is not in a permitted category.'))
