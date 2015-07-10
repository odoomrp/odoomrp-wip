# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, api


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    @api.multi
    def create_purchase_order(self):
        supplier_obj = self.env['res.partner']
        supplierinfo_obj = self.env['product.supplierinfo']
        # Start with all suppliers
        suppliers = supplier_obj.search([('supplier', '=', True)])
        for line in self.line_ids:
            sinfos = supplierinfo_obj.search(
                [('product_tmpl_id', '=', line.product_id.product_tmpl_id.id)])
            suppliers &= sinfos.mapped('name')
            # Stop condition to avoid the full loop if we don't have suppliers
            if not suppliers:
                break

        for supplier in suppliers:
            self.make_purchase_order(supplier.id)
