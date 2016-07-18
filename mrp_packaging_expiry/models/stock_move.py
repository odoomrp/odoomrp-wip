# -*- coding: utf-8 -*-
# © 2016 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api


class StockMove(models.Model):

    _inherit = 'stock.move'

    @api.multi
    def _get_expiry_dates(self, production):
        moves = (production.move_created_ids |
                 production.move_created_ids2.filtered(lambda x:
                                                       x.state != 'cancel'))
        lots = moves.mapped('lot_ids') | moves.mapped('restrict_lot_id')
        removal_lots = lots.filtered(lambda x: x.removal_date)
        removal_date = removal_lots and min(removal_lots.mapped(
            'removal_date')) or False
        life_lots = lots.filtered(lambda x: x.life_date)
        life_date = (life_lots and min(life_lots.mapped('life_date')) or
                     False)
        alert_lots = lots.filtered(lambda x: x.alert_date)
        alert_date = (alert_lots and min(alert_lots.mapped('alert_date')) or
                      False)
        use_lots = lots.filtered(lambda x: x.use_date)
        use_date = use_lots and min(use_lots.mapped('use_date')) or False
        return removal_date, life_date, alert_date, use_date

    @api.multi
    def action_done(self):
        for move in self.filtered(
                lambda x: x.production_id and x.production_id.production and
                x.restrict_lot_id):
            removal, life, alert, use = self._get_expiry_dates(
                move.production_id.production)
            move.restrict_lot_id.write({
                'removal_date': removal,
                'life_date': life,
                'alert_date': alert,
                'use_date': use
            })
        return super(StockMove, self).action_done()
