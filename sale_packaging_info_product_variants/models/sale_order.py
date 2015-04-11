# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.one
    @api.depends('order_id.product_ul', 'product_id', 'product_uom_qty',
                 'pri_pack', 'sec_pack')
    def _calculate_packages(self):
        # This cannot be done while https://github.com/odoo/odoo/issues/6276
        # is not resolved
        # if self.product_id:
        #     super(SaleOrderLine, self)._calculate_packages()
        # else:
        #     values = self.product_attributes.mapped('value')
        #     line_obj = self.with_context(attribute_values=values)
        #     super(SaleOrderLine, line_obj)._calculate_packages()
        super(SaleOrderLine, self)._calculate_packages()

    @api.one
    def _get_attributes_values(self):
        self.attributes_values = self.product_attributes.mapped('value')
