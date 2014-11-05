
from openerp import models, fields


class Machinery(models.Model):
    _inherit = 'machinery'

    purch_inv_line = fields.Many2one('account.invoice.line',
                                     string='Invoice Line')
