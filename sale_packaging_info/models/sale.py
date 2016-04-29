# -*- coding: utf-8 -*-
# © 2014-2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    product_ul = fields.Many2one(
        comodel_name='product.ul', string='Logistic Unit', readonly=True,
        states={'draft': [('readonly', False)]})

    @api.one
    @api.onchange('product_ul')
    def onchange_product_ul(self):
        for line in self.order_line:
            line.sec_pack = line.sec_pack or self.product_ul


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    pri_pack_qty = fields.Float(
        string='# Pkg 1', compute='_calculate_packages', digits=(12, 2),
        store=True)
    pri_pack = fields.Many2one(
        comodel_name='product.product', string='Pkg 1',
        compute='_calculate_packages')
    sec_pack_qty = fields.Float(
        string='# Pkg 2', compute='_calculate_packages', digits=(12, 2),
        store=True)
    sec_pack = fields.Many2one(
        comodel_name='product.ul', string='Pkg 2')
    # needed because of https://github.com/odoo/odoo/issues/6276
    attributes_values = fields.Many2many(
        comodel_name='product.attribute.value',
        compute='_get_attributes_values')

    @api.one
    def _get_attributes_values(self):
        try:
            self.attributes_values =\
                self.product_attribute_ids.mapped('value_id')
        except:
            self.attributes_values = self.product_id.attribute_value_ids

    @api.one
    @api.depends('product_id', 'product_uom_qty',
                 'pri_pack', 'sec_pack', 'attributes_values')
    def _calculate_packages(self):
        self.pri_pack = False
        self.pri_pack_qty = 0.0
        self.sec_pack_qty = 0.0
        if self.env.context.get('attribute_values'):
            # This is to allow to get values list from another source
            # (for example, for sale_product_variants, that doesn't have
            #  product_id filled)
            # It won't work while https://github.com/odoo/odoo/issues/6276
            # isn't solved
            attribute_values = self.env.context['attribute_values']
        elif self.attributes_values:
            attribute_values = self.attributes_values
        else:
            attribute_values = self.product_id.attribute_value_ids
        pack_attr_values = attribute_values.filtered("attribute_id.is_package")
        package_attr = pack_attr_values and pack_attr_values[0] or False
        if package_attr:
            self.pri_pack = package_attr.package_product
            if package_attr.numeric_value:
                self.pri_pack_qty = (
                    self.product_uom_qty / package_attr.numeric_value)
            if self.pri_pack:
                packaging = self.sec_pack.packagings.filtered(
                    lambda x: x.product == self.pri_pack)[:1]
                if packaging.ul_qty and packaging.rows:
                    self.sec_pack_qty = (self.pri_pack_qty /
                                         (packaging.ul_qty * packaging.rows))
