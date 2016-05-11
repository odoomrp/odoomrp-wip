# -*- coding: utf-8 -*-
# © 2015 Mikel Arregi - AvanzOSC
# © 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, exceptions, fields, models, _
from openerp.addons import decimal_precision as dp


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    pack = fields.One2many(
        comodel_name='packaging.operation', inverse_name='operation')
    expected_production = fields.One2many(
        comodel_name='mrp.production', inverse_name='production',
        string='Expected Production')
    production = fields.Many2one(
        comodel_name='mrp.production', string='Production')
    final_product_qty = fields.Float(
        string='Produced product qty', compute='_final_product_qty',
        digits=dp.get_precision('Product Unit of Measure'),
        help='This amount is the real amount produced in the MO.')
    left_product_qty = fields.Float(
        string='Qty left for packaging', compute='_left_product_qty',
        digits=dp.get_precision('Product Unit of Measure'),
        help='This amount is indicative, it is calculated with packaging'
        ' orders that are not in canceled state.')

    @api.multi
    @api.depends('move_created_ids2')
    def _final_product_qty(self):
        for record in self:
            moves = record.mapped('move_created_ids2').filtered(
                lambda x: x.state == 'done' and
                not x.location_dest_id.scrap_location and
                x.product_id == record.product_id)
            record.final_product_qty = sum(moves.mapped('product_uom_qty'))

    @api.multi
    @api.depends('final_product_qty', 'expected_production')
    def _left_product_qty(self):
        for record in self:
            moves = record.mapped('move_created_ids2').filtered(
                lambda x: x.state == 'done' and
                x.location_dest_id.scrap_location and
                x.product_id == record.product_id)
            remaining_qty = (record.final_product_qty -
                             sum(moves.mapped('product_uom_qty')))
            for production in record.expected_production.filtered(
                    lambda x: x.state != 'cancel'):
                product = production.production.product_id
                if production.move_lines2:
                    remaining_qty -= sum(production.move_lines2.filtered(
                        lambda m: m.product_id == product
                        ).mapped('product_uom_qty'))
                elif production.move_lines:
                    remaining_qty -= sum(production.move_lines.filtered(
                        lambda m: m.product_id == product
                        ).mapped('product_uom_qty'))
                else:
                    remaining_qty -= sum(production.product_lines.filtered(
                        lambda p: p.product_id == product
                        ).mapped('product_qty'))
            record.left_product_qty = remaining_qty

    @api.multi
    def get_dump_packages(self):
        self.ensure_one()
        pack_lines = []
        lines = self.env['mrp.bom.line'].search(
            ['|', ('product_tmpl_id', '=', self.product_tmpl_id.id),
             ('product_id', '=', self.product_id.id)])
        exist_prod = [x.product.id for x in self.pack]
        for line in lines:
            if line not in exist_prod:
                packs = filter(
                    lambda x: x not in exist_prod,
                    line.bom_id.product_tmpl_id.product_variant_ids.ids)
                pack_line = map(
                    lambda x: (0, 0, {'product': x}), packs)
                pack_lines.extend(pack_line)
        self.write({'pack': pack_lines})

    @api.one
    def recalculate_product_qty(self, qty, product):
        line = self.product_lines.filtered(
            lambda x: x.product_id == product or
            x.product_tmpl_id == product.product_tmpl_id)
        line.write({'product_qty': qty})

    @api.one
    def assign_parent_lot(self, production):
        line = self.product_lines.filtered(
            lambda x: x.product_id == production.product_id or
            x.product_tmpl_id == production.product_id.product_tmpl_id)
        line.write({'lot': (
                    production.move_created_ids2 and
                    production.move_created_ids2[0].restrict_lot_id.id or
                    False)})

    def _get_packaging_production_data(self, op_line):
        equal_uom = op_line.product.uom_id.id == self.product_id.uom_id.id
        final_product_qty = equal_uom and op_line.fill or op_line.qty
        data = self.product_id_change(op_line.product.id, final_product_qty)
        name = self.env['ir.sequence'].get('mrp.production.packaging')
        data['value'].update({'product_id': op_line.product.id,
                              'product_tmpl_id':
                              op_line.product.product_tmpl_id.id,
                              'product_qty': final_product_qty,
                              'name': name})
        try:
            data['value'].update({'project_id': self.project_id.id})
        except:
            # This is in case mrp_project module is installed
            pass
        return data['value']

    @api.one
    def create_mo_from_packaging_operation(self):
        for op in self.pack.filtered(lambda x: x.qty != 0 and not x.processed):
            linked_raw_products = []
            add_product = []
            production_vals = self._get_packaging_production_data(op)
            new_op = self.create(production_vals)
            new_op.action_compute()
            new_op.recalculate_product_qty(op.fill, self.product_id)
            new_op.assign_parent_lot(self)
            workorder = new_op.workcenter_lines[:1]
            for attr_value in op.product.attribute_value_ids:
                raw_product = attr_value.raw_product
                if raw_product:
                    value = self.get_new_components_info(
                        raw_product, op.qty, workorder)
                    linked_raw_products.append(value)
            for line in new_op.product_lines:
                if self.product_id.product_tmpl_id == line.product_tmpl_id:
                    if new_op.product_id.track_all or\
                            new_op.product_id.track_production:
                        for move in self.move_created_ids2:
                            if move.product_id == self.product_id:
                                line.lot = move.restrict_lot_id
                    line.product_id = self.product_id
                    new_op.manual_production_lot = line.lot.name
                    continue
            for link_product in linked_raw_products:
                recs = new_op.product_lines.filtered(
                    lambda x: x.product_id.id == link_product['product_id'])
                if recs:
                    recs.write(link_product)
                else:
                    add_product.append(link_product)
            new_op.write({
                'product_lines': map(lambda x: (0, 0, x), add_product),
                'production': self.id,
                'origin': self.name})
            op.packaging_production = new_op

    @api.multi
    def action_compute(self, properties=None):
        if not self.production:
            return super(MrpProduction, self).action_compute(properties)
        else:
            raise exceptions.Warning(_('You can not compute again the list.'))

    @api.multi
    def scrap_qty_left(self):
        self.ensure_one()
        if self.left_product_qty <= 0:
            raise exceptions.Warning(_('You can not scrap negative quantity.'))
        view_id = self.env.ref(
            'stock.view_stock_move_scrap_wizard')
        return {
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'stock.move.scrap',
            'views': [(view_id.id, 'form')],
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': self.with_context(
                active_ids=self.move_created_ids2.ids,
                active_id=self.move_created_ids2[:1].id,
                qty_left=self.left_product_qty).env.context,
        }

    @api.multi
    def produce_qty_left(self):
        self.ensure_one()
        if self.left_product_qty >= 0:
            raise exceptions.Warning(_('You have enough quantity to package.'))
        self._make_left_qty_produce_line()
        self.action_produce(self.id, abs(self.left_product_qty),
                            'consume_produce')

    @api.multi
    def _make_left_qty_produce_line(self):
        self.ensure_one()
        source_location_id = self.product_id.property_stock_production.id
        destination_location_id = self.location_dest_id.id
        procurement = self.env['procurement.order'].search(
            [('production_id', '=', self.id)])
        data = {
            'name': self.name,
            'date': self.date_planned,
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id,
            'product_uom_qty': abs(self.left_product_qty),
            'product_uos_qty': (
                self.product_uos and self.product_uos_qty or False),
            'product_uos': self.product_uos and self.product_uos.id or False,
            'location_id': source_location_id,
            'location_dest_id': destination_location_id,
            'move_dest_id': self.move_prod_id.id,
            'procurement_id': procurement[:1].id,
            'company_id': self.company_id.id,
            'production_id': self.id,
            'origin': self.name,
            'group_id': procurement[:1].group_id.id,
            'restrict_lot_id': (
                self.move_created_ids2[:1].restrict_lot_id.id or
                self.move_created_ids2[:1].lot_ids[:1].id),
        }
        move = self.env['stock.move'].create(data)
        move.action_confirm()


class PackagingOperation(models.Model):
    _name = 'packaging.operation'
    _rec_name = 'product'

    @api.multi
    @api.onchange('product', 'qty')
    def _calculate_weight(self):
        for record in self:
            value = record.mapped('product.attribute_value_ids').filtered(
                'raw_product')
            record.fill = (value[:1].numeric_value or 1) * record.qty

    @api.multi
    @api.onchange('fill')
    def _exceded_fill_quantity_warning(self):
        self.ensure_one()
        if self.fill > self.operation.left_product_qty:
            return {'warning':
                    {'title': _('Warning'),
                     'message': _("You won't be able to pack %f, there is only"
                                  " %f left" %
                                  (self.fill,
                                   self.operation.left_product_qty))}}
        return {}

    @api.multi
    @api.depends('packaging_production')
    def _is_processed(self):
        for record in self:
            record.processed = (record.packaging_production and
                                record.packaging_production.state != 'cancel')

    @api.multi
    @api.depends('product')
    def _compute_package_product(self):
        for record in self:
            record.package_product = record.product.attribute_value_ids.mapped(
                'raw_product')[:1]

    product = fields.Many2one(
        comodel_name='product.product', string='Product', required=True,
        help='Product that is going to be manufactured')
    operation = fields.Many2one(comodel_name='mrp.production')
    qty = fields.Integer(
        string='Qty', digits=dp.get_precision('Product Unit of Measure'),
        help='Product Quantity. It will be the new manufacturing order'
        ' quantity if dump uom is equal to product uom')
    fill = fields.Float(
        string='Fill', digits=dp.get_precision('Product Unit of Measure'),
        help='Product linked Raw Material value * Product Quantity. It will be'
        ' the new manufacturing order quantity if dump UoM is not equal to'
        ' product UoM')
    packaging_production = fields.Many2one(
        comodel_name='mrp.production', string='Packing manufacturing order')
    processed = fields.Boolean(
        string='Processed', compute='_is_processed')
    packing_state = fields.Selection(
        string='Packing MO State', related='packaging_production.state')
    package_product = fields.Many2one(
        comodel_name='product.product', string='Package Product',
        compute='_compute_package_product')

    @api.multi
    def write(self, values):
        ''' Do not change data if there is a related packaging order '''
        super(PackagingOperation,
              self.filtered(lambda x: not x.processed)).write(values)
