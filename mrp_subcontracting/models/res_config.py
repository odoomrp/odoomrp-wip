# -*- coding: utf-8 -*-
# © 2016 Jose Zambudio - Diagram Software S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class MrpConfigSettings(models.TransientModel):
    _inherit = 'mrp.config.settings'

    propagate_cancel = fields.Boolean(
        string='Propagate cancel (external procurements)',
        help='Automatically cancel the related purchase order when you cancel '
             'a manufacturing order of semi-finished product.')

    def _get_parameter(self, key, default=False):
        param_obj = self.env['ir.config_parameter']
        rec = param_obj.search([('key', '=', key)])
        return rec or default

    def _write_or_create_param(self, key, value):
        param_obj = self.env['ir.config_parameter']
        rec = self._get_parameter(key)
        if rec:
            if not value:
                rec.unlink()
            else:
                rec.value = value
        elif value:
            param_obj.create({'key': key, 'value': value})

    @api.multi
    def get_default_propagate_cancel(self):
        def get_value(key, default=''):
            rec = self._get_parameter(key)
            return rec and rec.value or default
        return {
            'propagate_cancel': get_value('propagate.cancel', False),
        }

    @api.multi
    def set_propagate_cancel(self):
        self._write_or_create_param('propagate.cancel',
                                    self.propagate_cancel)
