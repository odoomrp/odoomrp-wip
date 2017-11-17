# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, api, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.multi
    def show_pricelists(self):
        self.with_context(
            {'search_default_pricelist_type_id': 1}).browse(self.ids)
        result = self._get_act_window_dict(
            'product_pricelist_rules.pricelist_items_action')
        result['context'] = {'search_default_pricelist_type_id': 1,
                             'default_product_tmpl_id': self.id}
        result['domain'] = [('product_tmpl_id', '=', self.id)]
        return result

    @api.multi
    def _compute_count_pricelist(self):
        pricelist_model = self.env['product.pricelist.item']
        for record in self:
            domain = [('product_tmpl_id', '=', record.id)]
            record.count_pricelist = pricelist_model.search_count(domain)

    count_pricelist = fields.Integer(string="Count Pricelist",
                                     compute="_compute_count_pricelist")


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def show_pricelists(self):
        res = super(self.product_tmpl_id.__class__,
                    self.product_tmpl_id).show_pricelists()
        if res:
            res['context'] = {'search_default_pricelist_type_id': 1,
                              'default_product_id': self.id}
            res['domain'] = ['|', ('product_id', '=', self.id),
                             '&', ('product_tmpl_id', '=',
                                   self.product_tmpl_id.id),
                             ('product_id', '=', False)]
        return res

    @api.multi
    def _compute_count_pricelist(self):
        pricelist_model = self.env['product.pricelist.item']
        for record in self:
            domain = ['|', ('product_id', '=', record.id),
                      '&', ('product_tmpl_id', '=', record.product_tmpl_id.id),
                      ('product_id', '=', False)]
            record.count_pricelist = len(pricelist_model.search(domain))

    count_pricelist = fields.Integer(string="Count Pricelist",
                                     compute="_compute_count_pricelist")
