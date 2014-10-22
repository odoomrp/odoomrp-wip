
# -*- encoding: utf-8 -*-
##############################################################################
#
#    Daniel Campos (danielcampos@avanzosc.es) Date: 08/09/2014
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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


from openerp import models, fields


class MrpMachinery(models.Model):
    _name = "mrp.machinery"
    _description = "Holds records of Machines"

    def _def_company(self):
        return self.env.user.company_id.id

    name = fields.Char('Machine Name', required=True)
    company = fields.Many2one('res.company', 'Company', required=True,
                              default=_def_company)
    assetacc = fields.Many2one('account.account', string='Asset Account',
                               domain=[('user_type.code', '=', 'asset')])
    depracc = fields.Many2one('account.account', string='Depreciation Account')
    year = fields.Char('Year')
    model = fields.Char('Model')
    product = fields.Many2one('product.product', 'Associated product')
    serial_char = fields.Char('Product Serial #')
    serial = fields.Many2one('stock.production.lot', string='Product Serial #',
                             domain="[('product_id', '=', product)]")
    model_type = fields.Many2one('mrp.machine.model', 'Type')
    status = fields.Selection([('active', 'Active'), ('inactive', 'InActive'),
                               ('outofservice', 'Out of Service')],
                              'Status', required=True, default='active')
    ownership = fields.Selection([('own', 'Own'), ('lease', 'Lease'),
                                  ('rental', 'Rental')],
                                 'Ownership', default='own', required=True)
    bcyl = fields.Float('Base Cycles', digits=(16, 3),
                        help="Last recorded cycles")
    bdate = fields.Date('Record Date',
                        help="Date on which the cycles is recorded")
    purch_date = fields.Date('Purchase Date', help="Date of machine pruchase")
    purch_cost = fields.Float('Purchase Value', digits=(16, 2))
    purch_partner = fields.Many2one('res.partner', 'Purchased From')
    purch_inv = fields.Many2one('account.invoice', string='Purchase Invoice')
    purch_cycles = fields.Integer('Cycles at Purchase')
    actcycles = fields.Integer('Actual Cycles')
    deprecperc = fields.Float('Depreciation in %', digits=(10, 2))
    deprecperiod = fields.Selection([('monthly', 'Monthly'),
                                     ('quarterly', 'Quarterly'),
                                     ('halfyearly', 'Half Yearly'),
                                     ('annual', 'Yearly')], 'Depr. period',
                                    default='annual', required=True)
    primarymeter = fields.Selection([('calendar', 'Calendar'),
                                     ('cycles', 'Cycles'),
                                     ('hourmeter', 'Hour Meter')],
                                    'Primary Meter', default='cycles',
                                    required=True)
    warrexp = fields.Date('Date', help="Expiry date for warranty of product")
    warrexpcy = fields.Integer('(or) cycles',
                               help="Expiry cycles for warranty of product")
    location = fields.Many2one('stock.location', 'Stk Location',
                               help="This association is necessary if you want"
                               " to make repair orders with the machine")
    enrolldate = fields.Date('Enrollment date', required=True,
                             default=lambda
                             self: fields.Date.context_today(self))
    ambit = fields.Selection([('local', 'Local'), ('national', 'National'),
                              ('international', 'International')],
                             'Ambit', default='local', required=True)
    card = fields.Char('Card')
    cardexp = fields.Date('Card Expiration')
    frame = fields.Char('Frame Number')
    phone = fields.Char('Phone number')
    mac = fields.Char('MAC Address')
    insurance = fields.Char('Insurance Name')
    policy = fields.Char('Machine policy')
