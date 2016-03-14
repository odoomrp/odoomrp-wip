# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.one
    @api.depends('order_line', 'order_line.offer_id')
    def _calc_sale_promotion_gifts(self):
        self.sale_promotion_gifts.unlink()
        lines_with_price = self.order_line.filtered(lambda x: x.price_unit > 0)
        self.sale_promotion_gifts = [(6, 0, lines_with_price.mapped(
            'offer_id.sale_promotion_gifts.id'))]

    sale_promotion_gifts = fields.Many2many(
        comodel_name='sale.promotion.gift',
        string='Sale promotion gifts',
        compute='_calc_sale_promotion_gifts')
    sale_final_gifts = fields.One2many(
        'sale.final.gift', 'sale', string='Sale final gifts',
        copy=False)

    @api.one
    def action_button_confirm(self):
        sale_line_obj = self.env['sale.order.line']
        for line in self.sale_final_gifts:
            res = sale_line_obj.product_id_change(
                self.pricelist_id.id, line.product.id,
                partner_id=self.partner_id.id, date_order=self.date_order,
                fiscal_position=self.fiscal_position.id)
            vals = res['value']
            tax = [(6, 0, vals['tax_id'])]
            vals.update({'product_id': line.product.id,
                         'product_uom_qty': line.quantity,
                         'order_id': self.id,
                         'product_attributes': False,
                         'tax_id': tax,
                         'price_unit': 0.0
                         })
            sale_line_obj.create(vals)
        return super(SaleOrder, self).action_button_confirm()

    @api.multi
    def button_dump_sale_final_gifts(self):
        self.ensure_one()
        self.sale_final_gifts.unlink()
        for line in self.sale_promotion_gifts:
            vals = self._prepare_final_gift_product_data(line)
            if vals['quantity'] > 0:
                self.env['sale.final.gift'].create(vals)
        return True

    def _prepare_final_gift_product_data(self, gift_product):
        total_packs = 0
        sale_lines = self.order_line.filtered(
            lambda x: x.offer_id == gift_product.product_pricelist_item_offer)
        offer = gift_product.product_pricelist_item_offer
        total = offer.free_qty + offer.paid_qty
        if offer.not_combinable:
            for sale_line in sale_lines:
                qty = sale_line.product_uom_qty
                total_packs += qty // total
        else:
            item_list = set([x.item_id for x in sale_lines.filtered(
                lambda l: not l.offer_id.not_combinable)])
            for item in item_list:
                qty = 0
                if item.product_id:
                    qty = sum(
                        x.product_uom_qty for line in self.order_line.filtered(
                            lambda x: x.product_id == item.product_id and
                            not x.offer_id.not_combinable))
                elif item.product_tmpl_id:
                    qty = sum(
                        x.product_uom_qty for line in self.order_line.filtered(
                            lambda x: x.product_tmpl_id ==
                            item.product_tmpl_id and
                            not x.offer_id.not_combinable))
                elif item.categ_id:
                    qty = sum(
                        x.product_uom_qty for line in self.order_line.filtered(
                            lambda x: x.product_id.categ_id ==
                            item.categ_id and
                            not x.offer_id.not_combinable))
                else:
                    qty = sum(
                        x.product_uom_qty for line in sale_lines.filtered(
                            lambda x: not x.offer_id.not_combinable))
                total_packs += qty // total
        vals = {'sale': self.id,
                'product': gift_product.product.id,
                'quantity': total_packs * gift_product.quantity
                }
        return vals

    @api.one
    @api.constrains('sale_final_gifts')
    def check_sale_final_gifts(self):
        categorys = {}
        for line in self.sale_final_gifts:
            if line.category not in categorys:
                categorys[line.category] = {'quantity': line.quantity}
            else:
                category = categorys[line.category]
                sum_quantity = category.get('quantity') + line.quantity
                categorys[line.category] = {'quantity': sum_quantity}
        for category in categorys:
            datos_array = categorys[category]
            allowed = sum(
                x.quantity for x in self.sale_promotion_gifts.filtered(
                    lambda x: x.category == category))
            if datos_array['quantity'] > allowed:
                name = category.name
                raise exceptions.Warning(
                    _('Total Quantity %s, in final gift products with'
                      ' category %s, exceeds in gift products of the same'
                      ' category with amount %s') % (
                        str(datos_array['quantity']), name, str(allowed)))


class SalePromotionGift(models.Model):
    _name = 'sale.promotion.gift'
    _description = 'Sale promotion gift'

    product_pricelist_item_offer = fields.Many2one(
        'product.pricelist.item.offer', string='Pricelist item offer',
        copy=False, ondelete='cascade')
    product = fields.Many2one(
        'product.product', string='Product', required=True)
    category = fields.Many2one(
        'product.category', 'Category', related="product.categ_id",
        store=True, readonly=True)
    quantity = fields.Integer(string='Quantity', required=True)


class SaleFinalGift(models.Model):
    _name = 'sale.final.gift'
    _description = 'Sale final gift'

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
            exist = bool(self.sale.sale_promotion_gifts.filtered(
                lambda x: x.category == self.product.categ_id))
            if not exist:
                raise exceptions.Warning(
                    _('Error!: This product is not in a allowed category.'))
