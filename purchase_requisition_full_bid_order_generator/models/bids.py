# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, api, fields


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    @api.multi
    def _prepare_requisition_purchase_order_line(self, line, product, product_qty, purchase_id, supplier):
        po_line_obj = self.env['purchase.order.line']
        product_uom = self.env['product.uom']
        default_uom_po_id = product.uom_po_id.id
        date_order = self.ordering_date or fields.Datetime.now()
        qty = product_uom.browse(product.uom_id.id)._compute_qty(default_uom_po_id, product_qty)
        supplier_pricelist = supplier.property_product_pricelist_purchase and supplier.property_product_pricelist_purchase.id or False
        vals = po_line_obj.onchange_product_id(
            supplier_pricelist, product.id, qty, default_uom_po_id,
            supplier.id, date_order=date_order,
            fiscal_position_id=supplier.property_account_position.id,
            date_planned=line.schedule_date,
            name=False, price_unit=False, state='draft')['value']
        vals.update({
            'order_id': purchase_id,
            'product_id': product.id,
            'account_analytic_id': line.account_analytic_id.id,
            'taxes_id': [(6, 0, vals.get('taxes_id', []))],
        })
        return vals

    @api.multi
    def create_purchase_order(self):
        # Create RFQ to all suppliers with products they have from Requisition line
        if self.company_id.rfq_to_suppliers == 's':
            suppliers_dict = {}
            for line in self.line_ids:
                for supplier in line.product_id.seller_ids:
                    supplier_id = supplier.name.id
                    if supplier_id not in suppliers_dict.keys():
                        suppliers_dict[supplier_id] = [{line.product_id: line.product_qty}]
                    else:
                        if suppliers_dict[supplier_id][0].has_key(line.product_id):
                            suppliers_dict[supplier_id][0][line.product_id] = suppliers_dict[supplier_id][0][
                                                                                  line.product_id] + line.product_qty
                        else:
                            suppliers_dict[supplier_id].append({line.product_id: line.product_qty})

            for supplier, product_list in suppliers_dict.iteritems():
                res_partner = self.env['res.partner']
                supplier = res_partner.browse(supplier)
                # create purcahse order
                purchase = self.env['purchase.order'].create(self._prepare_purchase_order(self, supplier))
                for product_dict in product_list:
                    for product, qty in product_dict.iteritems():
                        # create purchase order line
                        line = self.env['purchase.requisition.line'].search(
                            [('product_id', '=', product.id), ('requisition_id', '=', self.id)], limit=1)
                        self.env['purchase.order.line'].create(
                            self._prepare_requisition_purchase_order_line(line, product, qty, purchase.id, supplier))
        else:
            # Create RFQ to the supplier which has all the products
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
