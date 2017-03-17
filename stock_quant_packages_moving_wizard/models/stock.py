# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models, _
from openerp.tools.float_utils import float_compare


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.multi
    def _prepare_move_to(self, dest_location):
        self.ensure_one()
        vals = {
            'name': '%s: Move to %s' % (
                self.product_id.name_get()[0][1],
                dest_location.complete_name),
            'product_id': self.product_id.id,
            'location_id': self.location_id.id,
            'location_dest_id': dest_location.id,
            'product_uom_qty': self.qty,
            'product_uom': self.product_id.uom_id.id,
            'date_expected': fields.Datetime.now(),
            'date': fields.Datetime.now(),
            'restrict_lot_id': self.lot_id.id,
            'origin': _('Quant Move'),
        }
        return vals

    @api.one
    def move_to(self, dest_location):
        # if the quant is reserved for another move,
        # we should cleanly un-reserve it first, so that
        # the picking that booked this quant comes back from
        # available to waiting availability
        if self.reservation_id:
            self.reservation_id.do_unreserve()
        vals = self._prepare_move_to(dest_location)
        new_move = self.env['stock.move'].create(vals)
        # No group has write access on stock.quant -> we need sudo()
        self.sudo().reservation_id = new_move
        new_move.with_context(quant_moving=True).action_done()

    @api.model
    def quants_get_prefered_domain(
            self, location, product, qty, domain=None,
            prefered_domain_list=[], restrict_lot_id=False,
            restrict_partner_id=False):
        quants = super(StockQuant, self).quants_get_prefered_domain(
            location, product, qty, domain=domain,
            prefered_domain_list=prefered_domain_list,
            restrict_lot_id=restrict_lot_id,
            restrict_partner_id=restrict_partner_id)
        if location.usage not in ['inventory', 'production', 'supplier']:
            return quants
        if self.env.context.get('quant_moving'):
            if domain is None:
                domain = []
            res_qty = qty
            if not prefered_domain_list:
                return self.quants_get(
                    location, product, qty, domain=domain,
                    restrict_lot_id=restrict_lot_id,
                    restrict_partner_id=restrict_partner_id)
            for prefered_domain in prefered_domain_list:
                res_qty_cmp = float_compare(
                    res_qty, 0, precision_rounding=product.uom_id.rounding)
                if res_qty_cmp > 0:
                    # try to replace the last tuple (None, res_qty) with
                    # something that wasn't chosen at first because of the
                    # prefered order
                    quants.pop()
                    tmp_quants = self.quants_get(
                        location, product, res_qty,
                        domain=domain + prefered_domain,
                        restrict_lot_id=restrict_lot_id,
                        restrict_partner_id=restrict_partner_id)
                    for quant in tmp_quants:
                        if quant[0]:
                            res_qty -= quant[1]
                    quants += tmp_quants
        return quants
