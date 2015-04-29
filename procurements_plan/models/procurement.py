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
        move_obj = self.env['stock.move']
        my_cursor = False
        untreated_procurements = {}
        untreated_moves = {}
        if 'procurement_ids' in self.env.context:
            print '*** entro 1'
            cond = [('id', 'not in', self.env.context['procurement_ids']),
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
        if 'procurement_ids' not in self.env.context:
            my_cursor = use_new_cursor
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

    def create_procurement_purchase_order(self, cr, uid, procurement, po_vals,
                                          line_vals, context=None):
        purchase_obj = self.pool['purchase.order']
        pur = super(ProcurementOrder, self).create_procurement_purchase_order(
            cr, uid, procurement, po_vals, line_vals, context=context)
        if procurement.plan:
            vals = {'plan': procurement.plan.id}
            purchase_obj.write(cr, uid, [pur], vals, context=context)
        return pur

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
