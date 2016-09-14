# -*- coding: utf-8 -*-
# (c) 2016 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api


class WorkcenterLineFinish(models.TransientModel):

    _inherit = "workcenter.line.finish"

    @api.multi
    def make_them_done(self):
        if ('active_id' in self.env.context and
                (self.env.context.get('active_model', False) ==
                 'mrp.production')):
            production_obj = self.env['mrp.production']
            production = production_obj.browse(self.env.context['active_id'])
            (production.move_lines | production.move_created_ids).action_done()
            production.signal_workflow('button_produce_close')
        else:
            return super(WorkcenterLineFinish, self).make_them_done()

    @api.multi
    def cancel_all(self):
        if ('active_id' in self.env.context and
                (self.env.context.get('active_model', False) ==
                 'mrp.production')):
            production_obj = self.env['mrp.production']
            production = production_obj.browse(self.env.context['active_id'])
            (production.move_lines |
             production.move_created_ids).action_cancel()
            production.signal_workflow('button_produce_close')
        else:
            return super(WorkcenterLineFinish, self).make_them_done()
