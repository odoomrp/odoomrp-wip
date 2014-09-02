# -*- encoding: utf-8 -*-
##############################################################################
#                                                                            #
#  OpenERP, Open Source Management Solution.                                 #
#                                                                            #
#  @author Carlos Sánchez Cifuentes <csanchez@grupovermon.com>               #
#                                                                            #
#  This program is free software: you can redistribute it and/or modify      #
#  it under the terms of the GNU Affero General Public License as            #
#  published by the Free Software Foundation, either version 3 of the        #
#  License, or (at your option) any later version.                           #
#                                                                            #
#  This program is distributed in the hope that it will be useful,           #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              #
#  GNU Affero General Public License for more details.                       #
#                                                                            #
#  You should have received a copy of the GNU Affero General Public License  #
#  along with this program. If not, see <http://www.gnu.org/licenses/>.      #
#                                                                            #
##############################################################################

from openerp import api, models, _


class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'

    #@api.onchange('product_id')
    #@api.one
    #def onchange_product(self):
        #homologation_obj = self.env['purchase.homologation']
        #homologations = homologation_obj.search([
            #(('partner_id', '=', self.order_id.partner_id.id),
             #('|',(('category_id', '=',
                    #self.product_id.product_tmpl_id.categ_id.id),
                   #('product_id', '=', False)),
              #(('category_id', '=', False),
               #('product_id', '=', self.product_id.id)))),
            #(('|', ('start_date', '<=', self.date_planned),
              #('start_date', '=', False)),
             #('|', ('end_date', '>=', self.date_planned),
              #('end_date', '=', False)))])
        #message = 'This product is not homologate for the selected supplier.'
        #if not homologations:
            #homologation_group_id = self.env.ref(
                #'purchase_homologation.group_purchase_homologation')
            #if not homologation_group_id in [
                #x.id for x in self.env.user.group_ids]:
                #raise Warning(_('Warning!'), _(message))

    @api.model
    def onchange_product_id(self, pricelist_id, product_id, qty, uom_id,
                            partner_id, date_order=False,
                            fiscal_position_id=False, date_planned=False,
                            name=False, price_unit=False, state='draft'):
        res = super(PurchaseOrderLine, self).onchange_product_id(
            self, pricelist_id, product_id, qty, uom_id, partner_id,
            date_order=date_order, fiscal_position_id=fiscal_position_id,
            date_planned=date_planned, name=name, price_unit=price_unit,
            state=state)
        product_obj = self.env['product.product']
        products = product_obj.search([('id', '=', product_id)])
        homologation_obj = self.env['purchase.homologation']
        homologations = homologation_obj.search([
            (('partner_id', '=', self.order_id.partner_id.id),
             ('|',
              (('category_id', '=', products[0].product_tmpl_id.categ_id.id),
               ('product_id', '=', False)),
              (('category_id', '=', False),
               ('product_id', '=', products[0].id)))),
            (('|', ('start_date', '<=', self.date_planned),
              ('start_date', '=', False)),
             ('|', ('end_date', '>=', self.date_planned),
              ('end_date', '=', False)))])
        message = 'This product is not homologate for the selected supplier.'
        if not homologations:
            homologation_group_id = self.env.ref(
                'purchase_homologation.group_purchase_homologation')
            if not homologation_group_id in [
                x.id for x in self.env.user.group_ids]:
                raise Warning(_('Warning!'), _(message))
        return res
