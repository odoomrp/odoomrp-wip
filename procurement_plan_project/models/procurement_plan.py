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


class ProcurementPlan(models.Model):

    _inherit = 'procurement.plan'

    @api.one
    def action_import(self):
        res = super(ProcurementPlan, self).action_import()
        procurements = self.procurement_ids
        procurements.write({'main_project_id': self.project_id.id})
        return res

    @api.multi
    def action_cancel(self):
        for plan in self:
            procurements = plan.procurement_ids
            procurements.write({'main_project_id': False})
        return super(ProcurementPlan, self).action_cancel()
