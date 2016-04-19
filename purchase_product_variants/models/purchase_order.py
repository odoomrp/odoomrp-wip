# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
from openerp.tools.float_utils import float_compare


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def wkf_confirm_order(self):
        """Create possible product variants not yet created."""
        for order in self:
            for line in order.order_line:
                if line.product_id or not line.product_template:
                    continue
                line._check_line_confirmability()
                product_obj = self.env['product.product']
                att_values_ids = line.product_attributes.mapped('value_id.id')
                domain = [('product_tmpl_id', '=', line.product_template.id)]
                for value in att_values_ids:
                    domain.append(('attribute_value_ids', '=', value))
                products = product_obj.search(domain)
                # Filter the product with the exact number of attributes values
                product = False
                for prod in products:
                    if len(prod.attribute_value_ids) == len(att_values_ids):
                        product = prod
                        break
                if not product:
                    product = product_obj.create(
                        {'product_tmpl_id': line.product_template.id,
                         'attribute_value_ids': [(6, 0, att_values_ids)]})
                line.write({'product_id': product.id})
        return super(PurchaseOrder, self).wkf_confirm_order()


class ProductAttributeValuePurchaseLine(models.Model):
    _name = 'purchase.order.line.attribute'

    purchase_line = fields.Many2one(
        comodel_name='purchase.order.line', string='Order line')
    attribute_id = fields.Many2one(
        comodel_name='product.attribute', string='Attribute',
        oldname="attribute")
    possible_values = fields.Many2many(
        comodel_name='product.attribute.value',
        compute='_get_possible_attribute_values', readonly=True)
    value_id = fields.Many2one(
        comodel_name='product.attribute.value', string='Value',
        domain="[('id', 'in', possible_values[0][2])]",
        oldname="value")

    @api.one
    @api.depends('attribute_id',
                 'purchase_line.product_template',
                 'purchase_line.product_template.attribute_line_ids')
    def _get_possible_attribute_values(self):
        attr_values = self.env['product.attribute.value']
        for attr_line in \
                self.purchase_line.product_template.attribute_line_ids:
            if attr_line.attribute_id.id == self.attribute_id.id:
                attr_values |= attr_line.value_ids
        self.possible_values = attr_values.sorted()


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_template = fields.Many2one(
        comodel_name='product.template', string='Product Template',
        domain="[('purchase_ok','=',True)]")
    product_attributes = fields.One2many(
        comodel_name='purchase.order.line.attribute',
        inverse_name='purchase_line', string='Product attributes', copy=True)
    order_state = fields.Selection(
        related='order_id.state', readonly=True)

    @api.model
    def _order_attributes(self, template, product_attribute_values):
        res = template._get_product_attributes_dict()
        res2 = []
        for val in res:
            value = product_attribute_values.filtered(
                lambda x: x.attribute_id.id == val['attribute_id'])
            if value:
                val['value_id'] = value
                res2.append(val)
        return res2

    def _get_product_description(self, template, product, product_attributes):
        name = product and product.name or template.name
        if not product_attributes and product:
            product_attributes = product.attribute_value_ids
        values = self._order_attributes(template, product_attributes)
        description = ", ".join([x['value_id'].name for x in values])
        if not description:
            return name
        return "%s (%s)" % (name, description)

    @api.multi
    @api.onchange('product_template')
    def onchange_product_template(self):
        self.ensure_one()
        res = {}
        self.name = self.product_template.name
        if self.product_template.description_purchase:
            self.name += '\n' + self.product_template.description_purchase
        if not self.product_template.attribute_line_ids:
            self.product_id = self.product_template.product_variant_ids[:1]
        else:
            self.product_id = False
            self.product_uom = self.product_template.uom_po_id
            self.product_uos = self.product_template.uos_id
            self.price_unit = self.order_id.pricelist_id.with_context(
                {'uom': self.product_uom.id,
                 'date': self.order_id.date_order}).template_price_get(
                self.product_template.id, self.product_qty or 1.0,
                self.order_id.partner_id.id)[self.order_id.pricelist_id.id]
        self.product_attributes = (
            [(2, x.id) for x in self.product_attributes] +
            [(0, 0, x) for x in
             self.product_template._get_product_attributes_dict()])
        # Get planned date and min quantity
        supplierinfo = False
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        for supplier in self.product_template.seller_ids:
            if supplier.name == self.order_id.partner_id:
                supplierinfo = supplier
                if supplierinfo.product_uom != self.product_uom:
                    res['warning'] = {
                        'title': _('Warning!'),
                        'message': _('The selected supplier only sells this '
                                     'product by %s') % (
                            supplierinfo.product_uom.name)
                    }
                min_qty = supplierinfo.product_uom._compute_qty(
                    supplierinfo.product_uom.id, supplierinfo.min_qty,
                    to_uom_id=self.product_uom.id)
                # If the supplier quantity is greater than entered from user,
                # set minimal.
                if (float_compare(
                        min_qty, self.product_qty,
                        precision_digits=precision) == 1):
                    if self.product_qty:
                        res['warning'] = {
                            'title': _('Warning!'),
                            'message': _('The selected supplier has a minimal '
                                         'quantity set to %s %s, you should '
                                         'not purchase less.') % (
                                supplierinfo.min_qty,
                                supplierinfo.product_uom.name)
                        }
                    self.product_qty = min_qty
        if not self.date_planned and supplierinfo:
            dt = fields.Datetime.to_string(
                self._get_date_planned(supplierinfo, self.order_id.date_order))
            self.date_planned = dt
        # Get taxes
        taxes = self.product_template.supplier_taxes_id
        self.taxes_id = self.order_id.fiscal_position.map_tax(taxes)
        res['domain'] = {'product_id': [('product_tmpl_id', '=',
                                         self.product_template.id)]}
        return res

    @api.one
    @api.onchange('product_attributes')
    def onchange_product_attributes(self):
        product_obj = self.env['product.product']
        att_values_ids = [attr_line.value_id.id
                          for attr_line in self.product_attributes]
        domain = [('product_tmpl_id', '=', self.product_template.id)]
        for value in att_values_ids:
            domain.append(('attribute_value_ids', '=', value))
        self.product_id = product_obj.search(domain, limit=1)
        if not self.product_id:
            self.name = self._get_product_description(
                self.product_template, False,
                self.product_attributes.mapped('value_id'))
            if self.product_template.description_purchase:
                self.name += '\n' + self.product_template.description_purchase

    @api.multi
    def onchange_product_id(
            self, pricelist_id, product_id, qty, uom_id, partner_id,
            date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, state='draft'):
        res = super(PurchaseOrderLine, self).onchange_product_id(
            pricelist_id, product_id, qty, uom_id, partner_id,
            date_order=date_order, fiscal_position_id=fiscal_position_id,
            date_planned=date_planned, name=name, price_unit=price_unit,
            state=state)
        if product_id:
            product_obj = self.env['product.product']
            product = product_obj.browse(product_id)
            attributes = [(0, 0, x) for x in
                          product._get_product_attributes_values_dict()]
            res['value_id'].update(
                {'product_attributes': attributes,
                 'product_template': product.product_tmpl_id.id})
        return res

    @api.multi
    def action_duplicate(self):
        self.ensure_one()
        self.copy()
        # Force reload of view as a workaround for lp:1155525
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'purchase.order',
            'res_id': self.order_id.id,
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def _check_line_confirmability(self):
        for line in self:
            if (any(not bool(attr_line.value_id) for attr_line
                    in line.product_attributes)):
                raise UserError(
                    _("You can not confirm before configuring all attribute "
                      "values."))
