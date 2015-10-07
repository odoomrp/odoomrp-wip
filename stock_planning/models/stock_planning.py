# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from dateutil.relativedelta import relativedelta


class StockPlanning(models.Model):

    _name = 'stock.planning'
    _description = 'Stock Planning'
    _order = 'id asc'

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
        move_obj = self.env['stock.move']
        proc_obj = self.env['procurement.order']
        purchase_line_obj = self.env['purchase.order.line']
        moves = move_obj._find_moves_from_stock_planning(
            self.company, self.scheduled_date, product=self.product,
            location_dest_id=self.location)
        self.move_incoming_to_date = sum(moves.mapped('product_uom_qty'))
        moves = moves.filtered(lambda x: x.date <= self.scheduled_date)
        if self.from_date:
            moves = moves.filtered(lambda x: x.date >= self.from_date)
        self.moves = [(6, 0, moves.ids)]
        states = ('confirmed', 'exception')
        procurements = proc_obj._find_procurements_from_stock_planning(
            self.company, self.scheduled_date, states=states,
            product=self.product, location_id=self.location,
            without_purchases=True)
        self.procurement_incoming_to_date = sum(
            procurements.mapped('product_qty'))
        procurements = procurements.filtered(
            lambda x: x.date_planned <= self.scheduled_date)
        if self.from_date:
            procurements = procurements.filtered(
                lambda x: x.date_planned >= self.from_date)
        self.procurements = [(6, 0, procurements.ids)]
        moves = move_obj._find_moves_from_stock_planning(
            self.company, self.scheduled_date, product=self.product,
            location_id=self.location)
        self.outgoing_to_date = sum(moves.mapped('product_uom_qty'))
        if self.from_date:
            moves = moves.filtered(lambda x: x.date >= self.from_date)
        self.outgoing_to_date_moves = [(6, 0, moves.ids)]
        lines = purchase_line_obj._find_purchase_lines_from_stock_planning(
            self.company, self.scheduled_date, self.product, self.location)
        self.incoming_in_po = sum(lines.mapped('product_qty'))
        lines = lines.filtered(lambda x: x.date_planned <= self.scheduled_date)
        if self.from_date:
            lines = lines.filtered(lambda x: x.date_planned >= self.from_date)
        purchase_orders = self.env['purchase.order']
        purchase_orders |= lines.mapped('order_id')
        self.purchases = [(6, 0, purchase_orders.ids)]
        self.scheduled_to_date = (
            self.qty_available + self.procurement_incoming_to_date +
            self.incoming_in_po + self.move_incoming_to_date -
            self.outgoing_to_date)

    @api.one
    def _get_rule(self):
        self.rule_min_qty = 0
        self.rule_max_qty = 0
        orderpoint_obj = self.env['stock.warehouse.orderpoint']
        cond = [('product_id', '=', self.product.id),
                ('location_id', '=', self.location.id)]
        orderpoints = orderpoint_obj.search(cond)
        self.rule_min_qty = orderpoints[:1].product_min_qty
        self.rule_max_qty = orderpoints[:1].product_max_qty

    @api.one
    def _get_required_increase(self):
        self.required_increase = 0
        if self.scheduled_to_date <= self.rule_min_qty:
            if self.rule_max_qty > self.scheduled_to_date:
                if self.scheduled_to_date >= 0:
                    self.required_increase = self.rule_max_qty
                else:
                    self.required_increase = ((self.scheduled_to_date * -1) +
                                              self.rule_max_qty)
            else:
                if self.scheduled_to_date >= 0:
                    self.required_increase = self.scheduled_to_date
                else:
                    self.required_increase = (self.scheduled_to_date * -1)
        elif self.scheduled_to_date > 0:
            if self.rule_min_qty == 0 and self.rule_max_qty == 0:
                self.required_increase = self.scheduled_to_date * -1
            elif (self.rule_max_qty == 0 and self.rule_min_qty >
                  self.scheduled_to_date):
                self.required_increase = (self.rule_min_qty -
                                          self.scheduled_to_date)
            elif (self.rule_max_qty > 0 and self.scheduled_to_date >
                  self.rule_max_qty):
                self.required_increase = (
                    (self.scheduled_to_date - self.rule_max_qty) * -1)
            else:
                self.required_increase = (
                    (self.scheduled_to_date - self.rule_min_qty) * -1)

    @api.one
    def _get_cost_price(self):
        self.cost_price = 0
        if self.required_increase > 0:
            self.cost_price = self.required_increase * self.unit_cost_price

    company = fields.Many2one('res.company', 'Company')
    location = fields.Many2one('stock.location', 'Location', translate=True)
    from_date = fields.Date('From Date')
    scheduled_date = fields.Date('Scheduled date')
    product = fields.Many2one('product.product', 'Product', translate=True)
    unit_cost_price = fields.Float(
        'Variant Cost Price', related='product.cost_price',
        digits_compute=dp.get_precision('Product Price'))
    category = fields.Many2one(
        'product.category', 'category', related='product.categ_id',
        store=True, translate=True)
    qty_available = fields.Float(
        'Quantity On Hand', compute='_get_product_info_location',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    virtual_available = fields.Float(
        'Forecast Quantity', compute='_get_product_info_location',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    incoming_qty = fields.Float(
        'Incoming', compute='_get_product_info_location',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    outgoing_qty = fields.Float(
        'Outgoing', compute='_get_product_info_location',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    move_incoming_to_date = fields.Float(
        'Incoming up to date from moves', compute='_get_to_date',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    moves = fields.Many2many(
        comodel_name='stock.move', string='Moves incoming to date',
        relation='rel_stock_planning_move', compute='_get_to_date',
        column1='stock_planning_id', column2='move_id')
    procurement_incoming_to_date = fields.Float(
        'Incoming up to date from procurements', compute='_get_to_date',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    procurements = fields.Many2many(
        comodel_name='procurement.order', string='Procurements',
        relation='rel_stock_planning_procurement', compute='_get_to_date',
        column1='stock_planning_id', column2='procurement_id')
    incoming_in_po = fields.Float(
        'Incoming in PO', compute='_get_to_date',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    purchases = fields.Many2many(
        comodel_name='purchase.order', relation='rel_stock_planning_purchase',
        column1='stock_planning_id', column2='purchase_id',
        string='Purchases', compute='_get_to_date')
    outgoing_to_date = fields.Float(
        'Outgoing to date', compute='_get_to_date',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    outgoing_to_date_moves = fields.Many2many(
        comodel_name='stock.move', relation='rel_outgoing_to_date_planning',
        column1='stock_planning_id', column2='move_id',
        string='Outgoin to date moves', compute='_get_to_date')
    scheduled_to_date = fields.Float(
        'Scheduled to date', compute='_get_to_date',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    rule_min_qty = fields.Float(
        'Rule min. qty', compute='_get_rule',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    rule_max_qty = fields.Float(
        'Rule max. qty', compute='_get_rule',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    required_increase = fields.Float(
        'Required increase', compute='_get_required_increase',
        digits_compute=dp.get_precision('Product Unit of Measure'))
    required_qty = fields.Float(
        'Required quantity', related='required_increase',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        store=True)
    cost_price = fields.Float(
        'Cost Price', compute='_get_cost_price',
        digits_compute=dp.get_precision('Product Price'))
    cost_price_required_increase = fields.Float(
        'Required increment Cost Price', related='cost_price', store=True,
        digits_compute=dp.get_precision('Product Price'))

    @api.multi
    def show_procurements(self):
        self.ensure_one()
        return {'name': _('Procurement orders'),
                'view_type': 'form',
                "view_mode": 'tree,form',
                'res_model': 'procurement.order',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', self.procurements.ids)]
                }

    @api.multi
    def show_purchases(self):
        self.ensure_one()
        return {'name': _('Purchase orders'),
                'view_type': 'form',
                "view_mode": 'tree,form',
                'res_model': 'purchase.order',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', self.purchases.ids)]
                }

    @api.multi
    def show_moves(self):
        self.ensure_one()
        return {'name': _('Moves'),
                'view_type': 'form',
                "view_mode": 'tree,form',
                'res_model': 'stock.move',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', self.moves.ids)]
                }

    @api.multi
    def show_outgoing_to_date_moves(self):
        self.ensure_one()
        return {'name': _('Outgoing to date moves'),
                'view_type': 'form',
                "view_mode": 'tree,form',
                'res_model': 'stock.move',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', self.outgoing_to_date_moves.ids)]
                }

    @api.multi
    def generate_procurement(self):
        self.ensure_one()
        procurement_obj = self.env['procurement.order']
        cond = [('location', '=', self.location.id),
                ('scheduled_date', '=', self.scheduled_date),
                ('product', '=', self.product.id),
                ('required_qty', '!=', 0)]
        lines = self.search(cond)
        for line in lines:
            vals = self._preparare_procurement_data_from_planning(line)
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

    @api.multi
    def _preparare_procurement_data_from_planning(self, line):
        vals = {'name': 'From stock scheduler',
                'origin': 'From stock scheduler',
                'product_id': line.product.id,
                'product_qty': line.required_qty,
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
                sorted_suppliers = sorted(suppliers[:1], reverse=True,
                                          key=lambda l: l.sequence)
                days_to_sum = (sorted_suppliers[0].delay or 0)
                break
        date = (fields.Date.from_string(line.scheduled_date) -
                (relativedelta(days=days_to_sum)))
        vals['date_planned'] = date
        return vals
