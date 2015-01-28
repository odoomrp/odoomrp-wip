# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class CrmClaim(models.Model):
    _inherit = 'crm.claim'

    @api.one
    @api.depends('ref')
    def _generate_ref_model_name(self):
        model_obj = self.env['ir.model']
        self.ref_model_name = False
        if self.ref:
            cond = [('model', '=', str(self.ref._model))]
            model = model_obj.search(cond)
            self.ref_model_name = model.name

    @api.one
    @api.depends('ref')
    def _generate_ref_name(self):
        self.ref_name = False
        if self.ref:
            self.ref_name = self.ref.name

    ref_model_name = fields.Char(
        string='Ref. Model', compute='_generate_ref_model_name', store=True)
    ref_name = fields.Char(
        string='Ref. Name', compute='_generate_ref_name', store=True)
