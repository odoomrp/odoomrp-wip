# -*- encoding: utf-8 -*-
##############################################################################
#
#    Avanzosc - Avanced Open Source Consulting
#    Copyright (C) 2011 - 2014 Avanzosc <http://www.avanzosc.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
from openerp.osv import orm, fields
from openerp import workflow


class RunSchedulerWithPlan(orm.TransientModel):
    _name = 'run.scheduler.with.plan'
    _description = 'Run Scheduler With Plan'

    _columns = {
        'plan_id': fields.many2one('procurement.plan', 'Plan', required=True)
    }

    def procure_calculation_plan(self, cr, uid, ids, context=None):
        for wiz in self.browse(cr, uid, ids, context):
            plan_id = wiz.plan_id.id
            workflow.trg_validate(uid, 'procurement.plan', plan_id,
                                  'button_run', cr)
        return {'type': 'ir.actions.act_window_close'}
