
from openerp import models, fields


class stock_pack_operation(models.Model):
    _inherit = "stock.pack.operation"

    machine = fields.Many2one('machinery', string='Machine')
