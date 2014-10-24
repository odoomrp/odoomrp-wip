
# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import api, models, fields


class MrpProduction(models.Model):

    _inherit = "mrp.production"

    pack = fields.One2many('download.operation', 'operation')
    claim = fields.Many2one('crm.claim')
    download_user = fields.Many2one('res.users')
    sample = fields.Many2many('mrp.sample')
    sample_taken = fields.Boolean('Samples Taken')


class DownloadOperation(models.Model):
    _name = "download.operation"
    _rec_name = 'product'

    @api.one
    def _calculate_weight(self):
        self.fill = self.ul.ul_qty * self.qty

    product = fields.Many2one('product.product', string='Product', required=True)
    operation = fields.Many2one('mrp.production')
    ref = fields.Many2one('stock.warehouse', string='Warehouse')
    qty = fields.Integer(string="QTY")
    fill = fields.Float(string="Fill", compute=_calculate_weight)
    lot = fields.Many2one('stock.production.lot')
    ul = fields.Many2one('product.ul', string='Ul')


class MrpSample(models.Model):
    _name = 'mrp.sample'

    name = fields.Char(string='Name')
