# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class AssignManualQuants(models.TransientModel):
    _inherit = 'assign.manual.quants'

    @api.model
    def default_get(self, var_fields):
        quant_obj = self.env['stock.quant']
        res = super(AssignManualQuants, self).default_get(
            var_fields=var_fields)
        quants_lines = []
        for line in res['quants_lines']:
            quant = quant_obj.browse(line['quant'])
            if not quant.locked:
                quants_lines.append(line)
        res['quants_lines'] = quants_lines
        return res
