
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

from openerp import models, fields


class Machinery(models.Model):
    _inherit = 'machinery'

    preop = fields.One2many('machine.prev.op', 'machine', 'Next Revisions')
    alert_list = fields.One2many('preventive.proceed', 'imachine', 'Alerts')
    pmaster_ids = fields.Many2many('preventive.master', 'machine_maint_rel',
                                   'machinery_id', 'preventive_master_id')
    order_list = fields.One2many('mrp.repair', 'idmachine',
                                 'Preventive Orders')
