# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, api, exceptions, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_supplier_info(self, product_tmpl_id, partner_type,
                               partnerinfo, min_qty=False, delay=False):
        values = {'name': partnerinfo,
                  'type': partner_type,
                  'product_tmpl_id': product_tmpl_id,
                  'min_qty': min_qty,
                  'delay': delay}
        return values

    @api.multi
    def button_customerinfo(self):
        self.ensure_one()
        model_data_obj = self.env['ir.model.data']
        PSupplierinfo = self.env['product.supplierinfo']
        PPartnerinfo = self.env['pricelist.partnerinfo']
        if not self.product_id:
            raise exceptions.Warning(_("There is no product to copy!"))
        else:
            customerinfo = PSupplierinfo.search(
                [('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),
                 ('name', '=', self.order_id.partner_id.id)])[:1]
            if not customerinfo:
                values = self._prepare_supplier_info(
                    self.product_id.product_tmpl_id.id, 'customer',
                    self.order_id.partner_id.id)
                customerinfo = PSupplierinfo.create(values)
            if not customerinfo.pricelist_ids:
                PPartnerinfo.create({'suppinfo_id': customerinfo.id,
                                     'min_quantity': self.product_uom_qty,
                                     'price': self.price_unit})
        model_datas = model_data_obj.search(
            [('model', '=', 'ir.ui.view'),
             ('name', '=', 'product_supplierinfo_edit_view')])
        context = self.env.context.copy()
        context['view_buttons'] = True
        return {
            'type': 'ir.actions.act_window',
            'name': 'Edit Product Customer',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'product.supplierinfo',
            'res_id': customerinfo.id,
            'context': context,
            'views': [(model_datas[0].res_id, 'form')],
            'target': 'new',
        }
