
from openerp import models, fields, api


class Machinery(models.Model):
    _inherit = 'machinery'

    asset = fields.Many2one('account.asset.asset', string='Asset')

    @api.one
    @api.depends('asset')
    def _asset_onchange(self):
        self.write(
            {'assetacc': self.asset.category_id.account_asset_id.id,
             'depracc': self.asset.category_id.account_depreciation_id.id
             })
