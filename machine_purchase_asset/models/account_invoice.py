
from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        acc_asset_obj = self.env['account.asset.asset']
        machinery_obj = self.env['machinery']
        res = super(AccountInvoice, self).invoice_validate()
        for invoice in self:
            asset_lst = acc_asset_obj.search([('code', '=', invoice.number)])
            if asset_lst:
                machinery_lst = machinery_obj.search([('purch_inv', '=',
                                                       invoice.id)])
                for machine in machinery_lst:
                    if machine.purch_inv_line.asset_category_id:
                        for asset in asset_lst:
                            if asset.name == machine.purch_inv_line.name:
                                machine.asset = asset.id
                                machine._asset_onchange()
        return res
