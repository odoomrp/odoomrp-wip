# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    plan = fields.Many2one('procurement.plan', string='Plan')

    @api.model
    def _procure_orderpoint_confirm(self, use_new_cursor=False,
                                    company_id=False):
        procurement_obj = self.env['procurement.order']
        move_obj = self.env['move.obj']
        my_cursor = False
        untreated_procurements = {}
        untreated_moves = {}
        if 'procurement_ids' not in self.env.context:
            my_cursor = use_new_cursor
        else:
            cond = [('id', 'not in', self.env.context['procurement_ids'].ids),
                    ('state', 'not in', ('cancel', 'done'))]
            procurements = procurement_obj.search(cond)
            for procurement in procurements:
                my_vals = {'id': procurement.id,
                           'state': procurement.state,
                           }
                untreated_procurements[(procurement.id)] = my_vals
                cond = [('procurement_id', '=', procurement.id)]
                moves = move_obj.search(cond)
                if moves:
                    for move in moves:
                        my_vals = {'id': move.id,
                                   'state': move.state,
                                   }
                        untreated_moves[(move.id)] = my_vals
                    self.env.cr.execute('update stock_move set state=%s'
                                        ' where id in %s',
                                        ('cancel', tuple(moves.ids)))
            if procurements:
                self.env.cr.execute('update procurement_order set state=%s'
                                    ' where id in %s',
                                    ('cancel', tuple(procurements.ids)))
        result = super(ProcurementOrder, self)._procure_orderpoint_confirm(
            use_new_cursor=my_cursor, company_id=company_id)
        if untreated_procurements:
            for data in untreated_procurements:
                datos_array = untreated_procurements[data]
                self.env.cr.execute('update procurement_order set state=%s'
                                    ' where id = %s', (datos_array['state'],
                                                       datos_array['id']))
        if untreated_moves:
            for data in untreated_moves:
                datos_array = untreated_moves[data]
                self.env.cr.execute('update stock_move set state=%s'
                                    ' where id = %s', (datos_array['state'],
                                                       datos_array['id']))
        return result

    @api.model
    def create(self, data):
        if 'plan' in self.env.context and 'plan' not in data:
            data.update({'plan': self.env.context.get('plan')})
        procurement = super(ProcurementOrder, self).create(data)
        return procurement

    @api.multi
    def button_remove_plan(self):
        template_obj = self.env['product.template']
        result = template_obj._get_act_window_dict(
            'procurements_plan.action_procurement_plan')
        result['domain'] = "[('id', '=', " + str(self.plan.id) + ")]"
        result['res_id'] = self.plan.id
        result['view_mode'] = 'form'
        result['views'] = []
        self.plan.write({'procurement_ids': [[3, self.id]]})
        return result

    @api.multi
    def button_run(self, autocommit=False):
        for procurement in self:
            procurement.with_context(plan=procurement.plan.id).run(
                autocommit=autocommit)
            procurement.plan._catch_purchases()
            procurement.plan._get_state()
        return True

    @api.multi
    def button_check(self, autocommit=False):
        for procurement in self:
            procurement.with_context(plan=procurement.plan.id).check(
                autocommit=autocommit)
            procurement.plan._catch_purchases()
            procurement.plan._get_state()
        return True

    @api.multi
    def cancel(self):
        super(ProcurementOrder, self).cancel()
        for procurement in self:
            if procurement.plan:
                procurement.plan._catch_purchases()
                procurement.plan._get_state()
        return True

    @api.multi
    def reset_to_confirmed(self):
        super(ProcurementOrder, self).reset_to_confirmed()
        for procurement in self:
            if procurement.plan:
                procurement.plan._catch_purchases()
                procurement.plan._get_state()
        return True
