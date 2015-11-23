# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def product_id_change(self, product_id, product_qty=0):
        product = self.env['product.product'].browse(product_id)
        warning = {}
        title = False
        message = False
        if product and product.mrp_production_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.mrp_production_warn_msg
            warning['title'] = title
            warning['message'] = message
            if product.mrp_production_warn == 'block':
                return {
                    'value': {
                        'product_id': False,
                        'product_uom': False,
                        'bom_id': False,
                        'routing_id': False,
                        'product_uos_qty': 0,
                        'product_uos': False
                    }, 'warning': warning}
        result = super(MrpProduction, self).product_id_change(
            product_id, product_qty=product_qty)
        if result.get('warning', False):
            warning['title'] = (
                title and title + ' & ' + result['warning']['title'] or
                result['warning']['title'])
            warning['message'] = (
                message and message + '\n\n' + result['warning']['message'] or
                result['warning']['message'])
        if warning:
            result['warning'] = warning
        return result
