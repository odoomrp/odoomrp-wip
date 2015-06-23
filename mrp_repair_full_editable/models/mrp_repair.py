# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api


class MrpRepair(models.Model):
    _inherit = 'mrp.repair'

    fees_lines = fields.One2many(readonly=False)
    operations = fields.One2many(readonly=False)
    invoice_method = fields.Selection(readonly=False)

    @api.multi
    @api.onchange('product_id')
    def onchange_product_id(self, product_id=None):
        res = super(MrpRepair, self).onchange_product_id(product_id)
        if not self.partner_id:
            res['value']['pricelist_id'] = self.env.ref('product.list0')
        return res
