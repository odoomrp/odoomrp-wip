# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _
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
        help='Date from which the interval starts counting days')
    days = fields.Integer(
        'Days interval', required=True,
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

    @api.multi
    def calculate_stock_planning(self):
        self.ensure_one()
        move_obj = self.env['stock.move']
        procurement_obj = self.env['procurement.order']
        planning_obj = self.env['stock.planning']
        planning = planning_obj.search([])
        planning.unlink()
        fdate = self.from_date
        from_date = False
        while fdate < self.to_date:
            product_datas = {}
            cond = [('company_id', '=', self.company.id),
                    ('date', '<=', fdate),
                    ('state', 'not in', ('done', 'cancel'))]
            if from_date:
                cond.append(('date', '>', from_date))
            if self.product:
                cond.append(('product_id', '>', self.product_id.id))
            moves = move_obj.search(cond).filtered(
                lambda x: x.location_id.usage == 'internal' or
                x.location_dest_id.usage == 'internal')
            if self.category:
                moves = moves.filtered(
                    lambda x: x.product_id.product_tmpl_id.categ_id.id ==
                    self.category.id)
            if self.template:
                moves = moves.filtered(
                    lambda x: x.product_id.product_tmpl_id.id ==
                    self.template.id)
            for move in moves:
                if move.location_id.usage == 'internal':
                    product_datas = self._find_product_in_table(
                        product_datas, move.product_id, move.location_id,
                        move.warehouse_id)
                if move.location_dest_id.usage == 'internal':
                    product_datas = self._find_product_in_table(
                        product_datas, move.product_id,
                        move.location_dest_id, move.warehouse_id)
            cond = [('company_id', '=', self.company.id),
                    ('date_planned', '<=', fdate),
                    ('state', 'in', ('confirmed', 'running'))]
            if from_date:
                cond.append(('date_planned', '>', from_date))
            if self.product:
                cond.append(('product_id', '>', self.product_id.id))
            procurements = procurement_obj.search(cond).filtered(
                lambda x: x.location_id.usage == 'internal')
            if self.category:
                procurements = procurements.filtered(
                    lambda x: x.product_id.product_tmpl_id.categ_id.id ==
                    self.category.id)
            if self.template:
                procurements = procurements.filtered(
                    lambda x: x.product_id.product_tmpl_id.id ==
                    self.template.id)
            for procurement in procurements:
                product_datas = self._find_product_in_table(
                    product_datas, procurement.product_id,
                    procurement.location_id, procurement.warehouse_id)
            for data in product_datas:
                datos_array = product_datas[data]
                vals = {'company': self.company.id,
                        'location': datos_array['location'].id,
                        'scheduled_date': fdate,
                        'product': datos_array['product'].id}
                if from_date:
                    vals['from_date'] = from_date
                if datos_array['warehouse']:
                    vals['warehouse'] = datos_array['warehouse'].id
                else:
                    cond = [('company_id', '=', self.company.id),
                            ('lot_stock_id', '=', datos_array['location'].id)]
                    warehouses = self.env['stock.warehouse'].search(cond)
                    if warehouses:
                        vals['warehouse'] = warehouses[0].id
                planning_obj.create(vals)
            from_date = fdate
            fdate = fields.Date.to_string(fields.Date.from_string(fdate) +
                                          relativedelta(days=self.days))
        return {'name': _('Stock Planning'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'stock.planning',
                }

    def _find_product_in_table(self, product_datas, product, location,
                               warehouse):
        found = False
        for data in product_datas:
            datos_array = product_datas[data]
            dproduct = datos_array['product']
            dlocation = datos_array['location']
            dwarehouse = datos_array['warehouse']
            if dproduct.id == product.id and dlocation.id == location.id:
                found = True
                if not dwarehouse and warehouse:
                    product_datas[data].update({'warehouse': warehouse})
                break
        if not found:
            my_vals = {'product': product,
                       'location': location,
                       'warehouse': warehouse,
                       }
            ind = product.id + location.id + (warehouse.id or 0)
            product_datas[(ind)] = my_vals
        return product_datas
