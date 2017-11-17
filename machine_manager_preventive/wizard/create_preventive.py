# -*- coding: utf-8 -*-
# Copyright 2016 Daniel Campos - Avanzosc S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
    def _default_prev_list(self):
        prev_op_ids = 'machi_prevs' in self.env.context and \
            self.env.context['machi_prevs'] or []
        return [(6, 0, prev_op_ids)]

    @api.multi
    def _default_op_count(self):
        return len(self.env.context.get('machi_prevs', 0))

    machi_prevs = fields.Many2many(
        comodel_name='preventive.machine.operation', inverse_name='machine',
        string='Machine Preventive Operations', default=_default_prev_list,
        readonly=True)
    op_count = fields.Integer(string='Number of operations',
                              default=_default_op_count, readonly=True)
