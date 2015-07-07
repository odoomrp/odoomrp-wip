# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    production_done = fields.Boolean(string="Production Done")

    @api.multi
    def test_production_done2(self):
        test = super(MrpProduction, self).test_production_done()
        if test and not self.production_done:
            self.production_done = True
        return False

    @api.multi
    def test_production_close(self):
        return True
