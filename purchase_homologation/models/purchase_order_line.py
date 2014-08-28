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

from openerp.osv import orm
from openerp.tools.translate import _

import exceptions


class PurchaseOrderLine(orm.Model):

    _inherit = 'purchase.order.line'

    def create(self, cr, uid, vals, context=None):
        purchase_order = self.pool['purchase.order']
        order_obj = purchase_order.browse(cr, uid, [vals['order_id']],
                                          context=context)
        product_product = self.pool['product.product']
        product_obj = product_product.browse(cr, uid, [vals['product_id']],
                                             context=context)
        res_partner_approval = self.pool['purchase.homologation']
        approval_ids = res_partner_approval.search(
            cr, uid, [('partner_id', '=', order_obj[0].partner_id.id),
                      ('category_id', '=',
                       product_obj[0].product_tmpl_id.categ_id.id),
                      ('start_date', '<', vals['date_planned']),
                      ('end_date', '>', vals['date_planned'])],
            context=context)
        if approval_ids is False:
            raise exceptions.Warning(
                _('Error!'),
                _("This product isn't homologate for the supplier selected."))
        return super(PurchaseOrderLine, self).create(
            cr, uid, vals, context=context)
