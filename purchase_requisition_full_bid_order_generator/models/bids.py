# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, api


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    @api.multi
    def create_purchase_order(self):
        partner_obj = self.env['res.partner']
        suppliers = partner_obj.search([('supplier', '=', True)])
        supplier_obj = self.env['product.supplierinfo']
        print suppliers
        suppliers_list = []
        for supplier in suppliers:
            all_products = True
            for line in self.line_ids:
                if not supplier_obj.search(
                        ['&', ('name', '=', supplier.id),
                         ('product_tmpl_id', '=', line.product_id.id)]):
                    all_products = False
            if all_products:
                print supplier.id
                suppliers_list.append(supplier.id)

        print suppliers_list

        for supplier in suppliers_list:
            self.make_purchase_order(supplier)

        return True
