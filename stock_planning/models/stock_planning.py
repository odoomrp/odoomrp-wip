# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _
import openerp.addons.decimal_precision as dp
from dateutil.relativedelta import relativedelta


class StockPlanning(models.Model):

    _name = 'stock.planning'
    _description = 'Stock Planning'
    _order = 'location, warehouse, product, scheduled_date'

    @api.one
    def _get_product_info_location(self):
        self.qty_available = 0
        self.virtual_available = 0
        self.incoming_qty = 0
        self.outgoing_qty = 0
        if self.product and self.location:
            prod = self.env['product.product'].with_context(
                {'location': self.location.id}).browse(self.product.id)
            self.qty_available = prod.qty_available
            self.virtual_available = prod.virtual_available
            self.incoming_qty = prod.incoming_qty
            self.outgoing_qty = prod.outgoing_qty

    @api.one
    def _get_to_date(self):
        self.incoming_to_date = 0
        self.outgoing_to_date = 0
        move_obj = self.env['stock.move']
        procurement_obj = self.env['procurement.order']
        move_qty = 0
        cond = [('company_id', '=', self.company.id),
                ('product_id', '=', self.product.id),
                ('date', '<=', self.scheduled_date),
                ('location_dest_id', '=', self.location.id),
                ('state', 'not in', ('done', 'cancel'))]
        if self.from_date:
            cond.append(('date', '>', self.from_date))
        moves = move_obj.search(cond)
        if moves:
            move_qty = sum(x.product_uom_qty for x in moves)
        procurement_qty = 0
        cond = [('company_id', '=', self.company.id),
                ('product_id', '=', self.product.id),
                ('date_planned', '<=', self.scheduled_date),
                ('location_id', '=', self.location.id),
                ('state', 'in', ('confirmed', 'running'))]
        if self.from_date:
            cond.append(('date_planned', '>', self.from_date))
        procurements = procurement_obj.search(cond)
        for procurement in procurements:
            if (not procurement.purchase_id or
                (procurement.purchase_id and procurement.purchase_id.state ==
                 'draft')):
                procurement_qty += procurement.product_qty
        self.incoming_to_date = move_qty + procurement_qty
        cond = [('company_id', '=', self.company.id),
                ('product_id', '=', self.product.id),
                ('date', '<=', self.scheduled_date),
                ('location_id', '=', self.location.id),
                ('state', 'not in', ('done', 'cancel'))]
        if self.from_date:
            cond.append(('date', '>', self.from_date))
        moves = move_obj.search(cond)
        if moves:
            self.outgoing_to_date = sum(x.product_uom_qty for x in moves)
        if not self.from_date:
            qty_available = self.qty_available
        else:
            qty_available = 0
            cond = [('company', '=', self.company.id),
                    ('warehouse', '=', self.warehouse.id or False),
                    ('location', '=', self.location.id),
                    ('scheduled_date', '<', self.scheduled_date),
                    ('product', '=', self.product.id)]
            lines = self.search(cond)
            if lines:
                line = max(lines, key=lambda x: x.scheduled_date)
                qty_available = line.scheduled_to_date
        if qty_available is not False:
            self.scheduled_to_date = (qty_available + self.incoming_to_date -
                                      self.outgoing_to_date)

    @api.one
    def _get_rule(self):
        self.rule_min_qty = 0
        self.rule_max_qty = 0
        orderpoint_obj = self.env['stock.warehouse.orderpoint']
        cond = [('product_id', '=', self.product.id),
                ('location_id', '=', self.location.id)]
        orderpoints = orderpoint_obj.search(cond)
        if orderpoints:
            self.rule_min_qty = orderpoints[0].product_min_qty
            self.rule_max_qty = orderpoints[0].product_max_qty

    @api.one
    def _get_required_increase(self):
        self.required_increase = 0
        if self.scheduled_to_date <= self.rule_min_qty:
            self.required_increase = self.rule_min_qty
            if self.scheduled_to_date < 0:
                self.required_increase = ((self.scheduled_to_date * -1) +
                                          self.rule_min_qty)
        elif self.scheduled_to_date > 0 and self.rule_max_qty == 0:
            if self.rule_min_qty == 0:
                self.required_increase = self.scheduled_to_date * -1
            elif self.rule_min_qty > self.scheduled_to_date:
                self.required_increase = (self.rule_min_qty -
                                          self.scheduled_to_date)
            else:
                self.required_increase = (
                    (self.scheduled_to_date - self.rule_min_qty) * -1)
        elif self.scheduled_to_date > 0 and self.rule_max_qty > 0:
            if self.scheduled_to_date > self.rule_max_qty:
                self.required_increase = (
                    (self.scheduled_to_date - self.rule_max_qty) * -1)
            else:
                self.required_increase = (
                    (self.scheduled_to_date - self.rule_min_qty) * -1)

    company = fields.Many2one('res.company', 'Company')
    warehouse = fields.Many2one('stock.warehouse', 'Warehouse')
    location = fields.Many2one('stock.location', 'Location', translate=True)
    from_date = fields.Date('From Date')
    scheduled_date = fields.Date('Scheduled date')
    product = fields.Many2one('product.product', 'Product', translate=True)
    category = fields.Many2one(
        'product.category', 'category', related='product.categ_id',
        store=True, translate=True)
    qty_available = fields.Float(
        'Quantity On Hand', compute=_get_product_info_location,
        digits_compute=dp.get_precision('Product Unit of Measure'))
    virtual_available = fields.Float(
        'Forecast Quantity', compute=_get_product_info_location,
        digits_compute=dp.get_precision('Product Unit of Measure'))
    incoming_qty = fields.Float(
        'Incoming', compute=_get_product_info_location,
        digits_compute=dp.get_precision('Product Unit of Measure'))
    outgoing_qty = fields.Float(
        'Outgoing', compute=_get_product_info_location,
        digits_compute=dp.get_precision('Product Unit of Measure'))
    incoming_to_date = fields.Float(
        'Incoming to date', compute=_get_to_date,
        digits_compute=dp.get_precision('Product Unit of Measure'))
    outgoing_to_date = fields.Float(
        'Outgoing to date', compute=_get_to_date,
        digits_compute=dp.get_precision('Product Unit of Measure'))
    scheduled_to_date = fields.Float(
        'Scheduled to date', compute=_get_to_date,
        digits_compute=dp.get_precision('Product Unit of Measure'))
    rule_min_qty = fields.Float(
        'Rule min. qty', compute=_get_rule,
        digits_compute=dp.get_precision('Product Unit of Measure'))
    rule_max_qty = fields.Float(
        'Rule max. qty', compute=_get_rule,
        digits_compute=dp.get_precision('Product Unit of Measure'))
    required_increase = fields.Float(
        'Required increase', compute=_get_required_increase,
        digits_compute=dp.get_precision('Product Unit of Measure'))
    required_qty = fields.Float(
        'Required quantity', related='required_increase',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        store=True)

    @api.multi
    def show_procurements(self):
        self.ensure_one()
        procurement_obj = self.env['procurement.order']
        cond = [('company_id', '=', self.company.id),
                ('product_id', '=', self.product.id),
                ('date_planned', '<=', self.scheduled_date),
                ('location_id', '=', self.location.id),
                ('state', 'in', ('confirmed', 'running'))]
        if self.from_date:
            cond.append(('date_planned', '>', self.from_date))
        procurements = procurement_obj.search(cond)
        if not procurements:
            raise exceptions.Warning(_('There are no procurements to show'))
        return {'name': _('Procurement orders'),
                'view_type': 'form',
                "view_mode": 'tree,form',
                'res_model': 'procurement.order',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', procurements.ids)]
                }

    @api.multi
    def generate_procurement(self):
        self.ensure_one()
        procurement_obj = self.env['procurement.order']
        cond = [('warehouse', '=', self.warehouse.id or False),
                ('location', '=', self.location.id),
                ('scheduled_date', '<=', self.scheduled_date),
                ('product', '=', self.product.id)]
        lines = self.search(cond)
        for line in lines:
            if line.required_qty == 0:
                continue
            vals = {'name': 'From stock scheduler',
                    'origin': 'From stock scheduler',
                    'product_id': line.product.id,
                    'product_qty': line.required_qty,
                    'warehouse_id': line.warehouse.id or False,
                    'location_id':  line.location.id,
                    'company_id': line.company.id,
                    }
            days_to_sum = 0
            for route in line.product.route_ids:
                if route.name == 'Manufacture':
                    days_to_sum = (line.product.produce_delay or 0)
                    break
                elif route.name == 'Buy':
                    suppliers = line.product.supplier_ids.filtered(
                        lambda x: x.type == 'supplier')
                    if suppliers:
                        sorted_suppliers = sorted(suppliers, reverse=True,
                                                  key=lambda l: l.sequence)
                        days_to_sum = (sorted_suppliers[0].delay or 0)
                    break
            date = (fields.Date.from_string(line.scheduled_date) -
                    (relativedelta(days=days_to_sum)))
            vals['date_planned'] = date
            vals.update(
                procurement_obj.onchange_product_id(line.product.id)['value'])
            procurement_obj.create(vals)
        return {'name': _('Stock Planning'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'stock.planning',
                'target': 'current',
                }
