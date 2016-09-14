# -*- coding: utf-8 -*-
# (c) 2016 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api, _


class MrpProduction(models.Model):

    _inherit = 'mrp.production'

    @api.multi
    def button_produce_close(self):
        res = {}
        move_list = self.move_lines.filtered(
            lambda x: x.state not in('cancel', 'done'))
        if move_list:
            idform = self.env.ref(
                'mrp_operations_extension.finish_wo_form_view')
            res = {
                'type': 'ir.actions.act_window',
                'name': _('Finish MO'),
                'res_model': 'workcenter.line.finish',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(idform.id, 'form')],
                'target': 'new',
                'context': self.env.context
                }
        else:
            self.signal_workflow('button_produce_close')
        return res
