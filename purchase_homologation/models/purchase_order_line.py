# -*- encoding: utf-8 -*-
##############################################################################
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

from openerp import models, _


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty,
                            uom_id, partner_id, date_order=False,
                            fiscal_position_id=False, date_planned=False,
                            name=False, price_unit=False, state='draft',
                            context=None):
        res = super(PurchaseOrderLine, self).onchange_product_id(
            cr, uid, ids, pricelist_id, product_id, qty, uom_id, partner_id,
            date_order=date_order, fiscal_position_id=fiscal_position_id,
            date_planned=date_planned, name=name, price_unit=price_unit,
            state=state, context=context)
        if not product_id:
            return res
        product_obj = self.pool['product.product']
        product = product_obj.browse(cr, uid, product_id, context=context)
        categ_ids = []
        categ = product.product_tmpl_id.categ_id
        while categ:
            categ_ids.append(categ.id)
            categ = categ.parent_id
        partner_obj = self.pool['res.partner']
        partner = partner_obj.browse(cr, uid, partner_id, context=context)
        homologation_obj = self.pool['purchase.homologation']
        homologation_ids = homologation_obj.search(
            cr, uid,
            ['|',
             ('partner_id', '=', False),
             ('partner_id', '=', partner.commercial_partner_id.id),
             '|',
             ('start_date', '<=', date_planned),
             ('start_date', '=', False),
             '|',
             ('end_date', '>=', date_planned),
             ('end_date', '=', False),
             '|',
             ('category_id', 'in', categ_ids),
             ('category_id', '=', False),
             '|',
             ('product_id', '=', product_id),
             ('product_id', '=', False)],
            context=context)
        message = _("This product is not homologated for purchasing it.")
        if not homologation_ids:
            res['warning'] = {
                'title': _('Error'),
                'message': _(message)
            }
            data_obj = self.pool['ir.model.data']
            xml_id = data_obj._get_id(cr, uid, 'purchase_homologation',
                                      'group_purchase_homologation')
            group_id = data_obj.read(cr, uid, xml_id, ['res_id'],
                                     context=context)['res_id']
            user = self.pool['res.users'].browse(cr, uid, uid, context=context)
            if group_id not in [x.id for x in user.groups_id]:
                # Block the use of that product
                return {'value': {'product_id': False},
                        'warning': res['warning']}
        return res
