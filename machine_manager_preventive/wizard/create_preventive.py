
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

from openerp import models, fields, api


class PreventiveCreateWizard(models.TransientModel):
    _name = 'preventive.create.wizard'
    _description = 'Create Machine Preventive operations'

    @api.multi
    def create_preventive(self):
        preventive_list = []
        machine_operations = self.env['preventive.machine.operation']
        master_operations = self.env['preventive.master']
        for master_op_id in self.env.context['active_ids']:
            prev_master = master_operations.browse(master_op_id)
            operation_list = prev_master.ope_material
            # Preventive operation match for preventive master operation list
            for operation in operation_list:
                op_name = operation.optype_id.name
                op_compose_name = '-'.join([prev_master.pmo_type.name, op_name,
                                           prev_master.machinemodel.name])
                # Preventive master operation name update
                if operation.name != op_compose_name:
                    operation.name = op_compose_name
                machine_list = prev_master.machinery_ids
                for machine in machine_list:  # Loop Preventive machine list
                    # Preventive machine operations(pmo) for current machine
                    machine_op_list = machine_operations.search(
                        [('machine', '=', machine.id)])
                    exist = bool(machine_op_list.filtered(
                        lambda x: x.opname_omm.id == operation.id))
                    if not exist:  # machine has no pmo
                        operation_name = '-'.join([op_compose_name,
                                                   machine.name])
                        res = {
                            'name': operation_name,
                            'opdescription': operation.description,
                            'opname_omm': operation.id,
                            'machine': machine.id,
                            'frequency': operation.frequency,
                            'interval_unit': operation.interval_unit,
                            'first_margin': operation.optype_id.margin_cy1,
                            'second_margin': operation.optype_id.margin_cy2,
                            'margin_fre1': operation.optype_id.margin_fre1,
                            'interval_unit1': (
                                operation.optype_id.interval_unit1),
                            'margin_fre2': operation.optype_id.margin_fre2,
                            'interval_unit2': (
                                operation.optype_id.interval_unit2),
                            'hours_qty': operation.hours_qty,
                            'last_hours_qty': operation.hours_qty,
                            }
                        if operation.basedoncy:  # Operation by cycles
                            res['cycles'] = operation.cycles
                            res['nextcycles'] = (operation.cycles +
                                                 machine.actcycles)
                            res['lastcycles'] = machine.actcycles
                        if operation.basedontime:  # Operation by date
                            today = fields.Date.today()
                            calc_date = machine_operations.get_interval_date(
                                today, operation.frequency,
                                operation.interval_unit)
                            # TODO last data operation calculation function
                            res['nextdate'] = calc_date
                            res['lastdate'] = today
                        if operation.cycles > 0 or operation.frequency > 0:
                            # Alarm check activation
                            res['check_al1'] = True
                            if (operation.optype_id.margin_cy2 != 0 or
                                    operation.optype_id.margin_fre2 != 0):
                                res['check_al2'] = True
                        prevent_oper = machine_operations.create(res)
                        preventive_list.append(prevent_oper.id)
        context = self.env.context.copy()
        context['machi_prevs'] = preventive_list
        wizard = {
            'type': 'ir.actions.act_window',
            'name': 'View Preventives',
            'res_model': 'preventive.list',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': context,
            }
        return wizard


class PreventiveList(models.TransientModel):
    """Create Machine Preventive operations """
    _name = 'preventive.list'
    _description = 'Preventive list'

    @api.multi
    def _prev_list(self):
        data = []
        machine_operations = self.env['preventive.machine.operation']
        if 'machi_prevs' in self.env.context:
            for prev_id in self.env.context['machi_prevs']:
                machi_pre = machine_operations.browse(prev_id)
                res = {
                    'name': machi_pre.name,
                    'opdescription': machi_pre.opdescription,
                    'machine': machi_pre.machine.id,
                    'cycles': machi_pre.cycles,
                    'first_margin': machi_pre.first_margin,
                    'second_margin': machi_pre.second_margin,
                    'frequency': machi_pre.frequency,
                    'interval_unit': machi_pre.interval_unit,
                    'margin_fre1': machi_pre.margin_fre1,
                    'interval_unit1': machi_pre.interval_unit1,
                    'margin_fre2': machi_pre.margin_fre2,
                    'interval_unit2': machi_pre.interval_unit2,
                    'nextdate': machi_pre.nextdate,
                    'nextcycles': machi_pre.nextcycles,
                    'last_hours_qty': machi_pre.last_hours_qty,
                    'hours_qty': machi_pre.hours_qty
                    }
                data.append(res)
        return data

    @api.multi
    def _op_count(self):
        return len(self.env.context.get('machi_prevs', 0))

    machi_prevs = fields.One2many('preventive.machine.operation', 'machine',
                                  'Machine Preventive Operations',
                                  default=_prev_list, readonly=True)
    op_count = fields.Integer('Number of operations', default=_op_count,
                              readonly=True)
