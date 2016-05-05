# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def wkf_confirm_order(self):
        """Create possible product variants not yet created."""
        product_obj = self.env['product.product']
        for line in self.mapped('order_line').filtered(
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
        return super(PurchaseOrder, self).wkf_confirm_order()


class PurchaseOrderLine(models.Model):
    _inherit = ['purchase.order.line', 'product.configurator']
    _name = 'purchase.order.line'

    order_state = fields.Selection(
        related='order_id.state', readonly=True)
    # Needed for getting the lang variable for translating descriptions
    partner_id = fields.Many2one(related='order_id.partner_id', readonly=True)

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
    def onchange_product_id(
            self, pricelist_id, product_id, qty, uom_id, partner_id,
            date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, state='draft'):
        res = super(PurchaseOrderLine, self).onchange_product_id(
            pricelist_id, product_id, qty, uom_id, partner_id,
            date_order=date_order, fiscal_position_id=fiscal_position_id,
            date_planned=date_planned, name=name, price_unit=price_unit,
            state=state)
        new_value = self.onchange_product_id_product_configurator_old_api(
            product_id=product_id, partner_id=partner_id)
        value = res.setdefault('value', {})
        value.update(new_value)
        if product_id:
            product_obj = self.env['product.product']
            if partner_id:
                partner = self.env['res.partner'].browse(partner_id)
                product_obj = product_obj.with_context(lang=partner.lang)
            prod = product_obj.browse(product_id)
            if prod.description_purchase:
                value['name'] += '\n' + prod.description_purchase
        return res
