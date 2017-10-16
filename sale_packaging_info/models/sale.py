# -*- coding: utf-8 -*-
# © 2014-2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models
from openerp.addons import decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    product_ul_id = fields.Many2one(
        comodel_name='product.ul', string='Logistic Unit', readonly=True,
        states={'draft': [('readonly', False)]})

    @api.multi
    @api.onchange('product_ul_id')
    def onchange_product_ul_id(self):
        for record in self:
            for line in record.order_line:
                line.sec_pack_id = line.sec_pack_id or record.product_ul_id


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    pri_pack_qty = fields.Float(
        string='# Pkg 1', compute='_calculate_packages',
        digits=dp.get_precision('Product Unit of Measure'), store=True)
    pri_pack_id = fields.Many2one(
        comodel_name='product.product', string='Pkg 1',
        compute='_calculate_packages')
    sec_pack_qty = fields.Float(
        string='# Pkg 2', compute='_calculate_packages',
        digits=dp.get_precision('Product Unit of Measure'), store=True)
    sec_pack_id = fields.Many2one(
        comodel_name='product.ul', string='Pkg 2')
    # needed because of https://github.com/odoo/odoo/issues/6276
    attributes_value_ids = fields.Many2many(
        comodel_name='product.attribute.value',
        compute='_get_attributes_values')

    @api.multi
    def _get_attributes_values(self):
        for record in self:
            try:
                record.attributes_value_ids =\
                    record.product_attribute_ids.mapped('value_id')
            except:
                record.attributes_value_ids =\
                    record.product_id.attribute_value_ids

    @api.depends('product_id', 'product_uom_qty',
                 'pri_pack_id', 'sec_pack_id', 'attributes_value_ids')
    def _calculate_packages(self):
        for record in self:
            record.pri_pack_id = False
            record.pri_pack_qty = 0.0
            record.sec_pack_qty = 0.0
            if self.env.context.get('attribute_values'):
                # This is to allow to get values list from another source
                # (for example, for sale_product_variants, that doesn't have
                #  product_id filled)
                # It won't work while https://github.com/odoo/odoo/issues/6276
                # isn't solved
                attribute_values = self.env.context['attribute_values']
            elif record.attributes_value_ids:
                attribute_values = record.attributes_value_ids
            else:
                attribute_values = record.product_id.attribute_value_ids
            pack_attr_values = attribute_values.filtered(
                "attribute_id.is_package")
            package_attr = pack_attr_values and pack_attr_values[0] or False
            if package_attr:
                record.pri_pack_id = package_attr.package_product_id
                if package_attr.numeric_value:
                    record.pri_pack_qty = (
                        record.product_uom_qty / package_attr.numeric_value)
                if record.pri_pack_id:
                    packaging = record.sec_pack_id.packagings.filtered(
                        lambda x: x.product_id == record.pri_pack_id)[:1]
                    if packaging.ul_qty and packaging.rows:
                        record.sec_pack_qty = (
                            record.pri_pack_qty /
                            (packaging.ul_qty * packaging.rows))
