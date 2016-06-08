# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _
from dateutil.relativedelta import relativedelta


class WizStockPlanning(models.TransientModel):

    _name = 'wiz.stock.planning'
    _description = 'Wiz Stock Planning'

    @api.multi
    def _def_company(self):
        return self.env.user.company_id.id

    company = fields.Many2one(
        'res.company', 'Company', default=_def_company, required=True)
    from_date = fields.Date(
        'From date', required=True,
        default=lambda self: fields.Date.context_today(self),
        help='Date from which the interval starts counting days')
    days = fields.Integer(
        'Days interval', required=True, default=1,
        help='Increase number of days starting from the date from')
    to_date = fields.Date('To date', required=True,
                          help='Deadline for calculating periods')
    category = fields.Many2one(
        'product.category', 'Category',
        help='Enter this field if you want to filter by category')
    template = fields.Many2one(
        'product.template', 'Template',
        help='Enter this field if you want to filter by template')
    product = fields.Many2one(
        'product.product', 'Product',
        help='Enter this field if you want to filter by product')
    locations = fields.Many2many(
        comodel_name='stock.location', relation='rel_stock_planning_location',
        column1='wiz_stock_planning_id', column2='locations_id',
        string='Locations')

    @api.multi
    def calculate_stock_planning(self):
        self.ensure_one()
        planning_obj = self.env['stock.planning']
        move_obj = self.env['stock.move']
        proc_obj = self.env['procurement.order']
        if self.days < 1:
            raise exceptions.Warning(
                _('Error!: Increase number of days must be greater than zero'))
        cond = [('company', '=', self.company.id)]
        if self.locations:
            cond.append(('location', 'in', self.locations.ids))
        if self.product:
            cond.append(('product', '=', self.product.id))
        planning = planning_obj.search(cond)
        planning.unlink()
        fdate = self.from_date
        product_datas = {}
        while fdate < self.to_date:
            fdate = fields.Date.to_string(fields.Date.from_string(fdate) +
                                          relativedelta(days=self.days))
        fdate = fields.Date.to_string(fields.Date.from_string(fdate) -
                                      relativedelta(days=self.days))
        for move in move_obj._find_moves_from_stock_planning(
            self.company, fdate, category=self.category,
                template=self.template, product=self.product):
            if move.location_id.usage == 'internal':
                if (not self.locations or
                    (self.locations and move.location_id.id in
                     self.locations.ids)):
                    product_datas = self._find_product_in_table(
                        product_datas, move.product_id, move.location_id)
            if move.location_dest_id.usage == 'internal':
                if (not self.locations or
                    (self.locations and move.location_dest_id.id in
                     self.locations.ids)):
                    product_datas = self._find_product_in_table(
                        product_datas, move.product_id, move.location_dest_id)
        for procurement in proc_obj._find_procurements_from_stock_planning(
            self.company, fdate, category=self.category,
                template=self.template, product=self.product, periods=True):
            if (not self.locations or
                (self.locations and procurement.location_id.id in
                 self.locations.ids)):
                product_datas = self._find_product_in_table(
                    product_datas, procurement.product_id,
                    procurement.location_id)
        self._generate_stock_planning(product_datas)
        return {'name': _('Stock Planning'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'stock.planning',
                }

    def _find_product_in_table(self, product_datas, product, location):
        found = False
        for data in product_datas:
            datos_array = product_datas[data]
            dproduct = datos_array['product']
            dlocation = datos_array['location']
            if dproduct.id == product.id and dlocation.id == location.id:
                found = True
        if not found:
            my_vals = {'product': product,
                       'location': location,
                       }
            ind = product.id + location.id
            product_datas[(ind)] = my_vals
        return product_datas

    def _generate_stock_planning(self, product_datas):
        planning_obj = self.env['stock.planning']
        for data in product_datas:
            datos_array = product_datas[data]
            fdate = self.from_date
            from_date = False
            while fdate < self.to_date:
                vals = {'company': self.company.id,
                        'location': datos_array['location'].id,
                        'scheduled_date': fdate,
                        'product': datos_array['product'].id}
                if from_date:
                    vals['from_date'] = from_date
                planning_obj.create(vals)
                from_date = fields.Date.to_string(
                    fields.Date.from_string(fdate) + relativedelta(days=1))
                fdate = fields.Date.to_string(fields.Date.from_string(fdate) +
                                              relativedelta(days=self.days))
