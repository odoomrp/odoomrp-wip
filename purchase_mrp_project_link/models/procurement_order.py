# -*- encoding: utf-8 -*-
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
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, api


class ProcurementOrder(models.Model):

    _inherit = 'procurement.order'

    @api.multi
    def set_main_project(self):
        mto_record = self.env.ref('stock.route_warehouse0_mto')
        result = super(ProcurementOrder, self).set_main_project()
        for record in self:
            if mto_record in record.product_id.route_ids:
                if record.main_project_id:
                    main_project = record.main_project_id.id
                    if record.purchase_id:
                        purchase = record.purchase_id
                        purchase.main_project_id = main_project
        return result
