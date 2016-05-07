# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class StockMove(models.Model):
    _inherit = ["stock.move", "product.configurator"]
    _name = "stock.move"

    create_variant = fields.Boolean(
        help="Mark this check if you want to auto-create the variant when "
             "saving the stock move. Otherwise, you will need to specify "
             "a product variant.")

    @api.multi
    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        res = super(StockMove, self).onchange_product_tmpl_id()
        if res.get('domain', {}).get('product_id'):
            res['domain']['product_id'].append(('type', '!=', 'service'))
        return res

    @api.multi
    @api.onchange('product_attribute_ids')
    def onchange_product_attribute_ids(self):
        res = super(StockMove, self).onchange_product_attribute_ids()
        if res.get('domain', {}).get('product_id'):
            res['domain']['product_id'].append(('type', '!=', 'service'))
        return res

    @api.multi
    def onchange_product_id(self, prod_id=False, loc_id=False,
                            loc_dest_id=False, partner_id=False):
        res = super(StockMove, self).onchange_product_id(
            prod_id=prod_id, loc_id=loc_id, loc_dest_id=loc_dest_id,
            partner_id=partner_id)
        new_value = self.onchange_product_id_product_configurator_old_api(
            product_id=prod_id)
        value = res.setdefault('value', {})
        value.update(new_value)
        return res

    @api.multi
    def button_show_attributes(self):
        for move in self:
            if not move.product_id:
                move.with_context(
                    not_reset_product=True).onchange_product_tmpl_id()
            else:
                move.onchange_product_id_product_configurator()

    @api.model
    def create(self, vals):
        if vals.get('create_variant') and not vals.get('product_id'):
            vals = self._create_variant_from_vals(vals)
        return super(StockMove, self).create(vals)

    @api.multi
    def write(self, vals):
        create_variant = (vals.get(
            'create_variant', all(self.mapped('create_variant'))) if self
            else False)
        if create_variant:
            for move in self:
                product_id = vals.get('product_id', move.product_id.id)
                if not product_id:
                    vals = self._create_variant_from_vals(vals)
        return super(StockMove, self).write(vals)
