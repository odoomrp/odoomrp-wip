# -*- coding: utf-8 -*-
# © 2014-2016 Oihane Crucelaegui - AvanzOSC
# © 2015-2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models
from lxml import etree


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        """Avoid to have 2 times the field product_tmpl_id, as modules like
        sale_stock adds this field as invisible, so we can't trust the order
        of them. We also override the modifiers to avoid a readonly field.
        """
        res = super(SaleOrder, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if view_type != 'form':
            return res  # pragma: no cover
        if 'order_line' not in res['fields']:
            return res  # pragma: no cover
        line_field = res['fields']['order_line']
        if 'form' not in line_field['views']:
            return res  # pragma: no cover
        view = line_field['views']['form']
        eview = etree.fromstring(view['arch'])
        fields = eview.xpath("//field[@name='product_tmpl_id']")
        field_added = False
        for field in fields:
            if field.get('invisible') or field_added:
                field.getparent().remove(field)
            else:
                # Remove modifiers that makes the field readonly
                field.set('modifiers', "")
                field_added = True
        view['arch'] = etree.tostring(eview)
        return res


class SaleOrderLine(models.Model):
    _inherit = ["sale.order.line", "product.configurator"]
    _name = "sale.order.line"

    order_state = fields.Selection(related='order_id.state', readonly=True)
    # Needed for getting the lang variable for translating descriptions
    partner_id = fields.Many2one(related='order_id.partner_id', readonly=True)

    @api.multi
    def product_id_change(
            self, pricelist, product, qty=0, uom=False, qty_uos=0,
            uos=False, name='', partner_id=False, lang=False, update_tax=True,
            date_order=False, packaging=False, fiscal_position=False,
            flag=False):
        res = super(SaleOrderLine, self).product_id_change(
            pricelist, product, qty=qty, uom=uom, qty_uos=qty_uos, uos=uos,
            name=name, partner_id=partner_id, lang=lang, update_tax=update_tax,
            date_order=date_order, packaging=packaging,
            fiscal_position=fiscal_position, flag=flag)
        new_value = self.onchange_product_id_product_configurator_old_api(
            product_id=product, partner_id=partner_id)
        value = res.setdefault('value', {})
        value.update(new_value)
        if product:
            product_obj = self.env['product.product']
            if partner_id:
                partner = self.env['res.partner'].browse(partner_id)
                product_obj = product_obj.with_context(lang=partner.lang)
            prod = product_obj.browse(product)
            if prod.description_sale:
                value['name'] += '\n' + prod.description_sale
        return res

    @api.multi
    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        res = super(SaleOrderLine, self).onchange_product_tmpl_id()
        if self.product_tmpl_id.attribute_line_ids:
            self.product_uom = self.product_tmpl_id.uom_id
            self.product_uos = self.product_tmpl_id.uos_id
            self.price_unit = self.order_id.pricelist_id.with_context(
                {'uom': self.product_uom.id,
                 'date': self.order_id.date_order}).template_price_get(
                self.product_tmpl_id.id, self.product_uom_qty or 1.0,
                self.order_id.partner_id.id)[self.order_id.pricelist_id.id]
        # Update taxes
        fpos = self.order_id.fiscal_position
        if not fpos:
            fpos = self.order_id.partner_id.property_account_position
        self.tax_id = fpos.map_tax(self.product_tmpl_id.taxes_id)
        return res

    @api.multi
    def action_duplicate(self):
        for line in self:
            line.copy()

    @api.multi
    def button_confirm(self):
        product_obj = self.env['product.product']
        for line in self.filtered(
                lambda x: not x.product_id and x.product_tmpl_id):
            product = product_obj._product_find(
                line.product_tmpl_id, line.product_attribute_ids)
            if not product:
                product = product_obj.create({
                    'product_tmpl_id': line.product_tmpl_id.id,
                    'attribute_value_ids':
                        [(6, 0,
                          line.product_attribute_ids.mapped('value_id').ids)]})
            line.write({'product_id': product.id})
        super(SaleOrderLine, self).button_confirm()

    @api.multi
    def update_price_unit(self):
        self.ensure_one()
        if not self.product_id:
            price_extra = 0.0
            for attr_line in self.product_attribute_ids:
                price_extra += attr_line.price_extra
            self.price_unit = self.order_id.pricelist_id.with_context({
                'uom': self.product_uom.id,
                'date': self.order_id.date_order,
                'price_extra': price_extra,
            }).template_price_get(
                self.product_tmpl_id.id, self.product_uom_qty or 1.0,
                self.order_id.partner_id.id)[self.order_id.pricelist_id.id]

    def _auto_init(self, cr, context=None):
        # Avoid the removal of the DB column due to sale_stock defining
        # this field as a related non stored one
        if self._columns.get('product_tmpl_id'):
            self._columns['product_tmpl_id'].store = True
            self._columns['product_tmpl_id'].readonly = False
        super(SaleOrderLine, self)._auto_init(cr, context=context)
