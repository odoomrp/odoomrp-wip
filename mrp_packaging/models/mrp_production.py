# -*- coding: utf-8 -*-
# (c) 2015 Mikel Arregi - AvanzOSC
# (c) 2015 Oihane Crucelaegui - AvanzOSC
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
                lambda x: x.state == 'done')
            record.final_product_qty = sum(moves.mapped('product_uom_qty'))

    @api.one
    @api.depends('final_product_qty', 'expected_production')
    def _left_product_qty(self):
        left_qty = self.final_product_qty
        for production in self.expected_production:
            if production.state != 'cancel':
                if production.move_lines2:
                    for move in production.move_lines2:
                        if production.production.product_id == move.product_id:
                            left_qty -= move.product_uom_qty
                elif production.move_lines:
                    for move in production.move_lines:
                        if production.production.product_id == move.product_id:
                            left_qty -= move.product_uom_qty
                else:
                    for product in production.product_lines:
                        if (production.production.product_id ==
                                product.product_id):
                            left_qty -= product.product_qty
        self.left_product_qty = left_qty

    @api.one
    def get_dump_packages(self):
        pack_lines = []
        lines = self.env['mrp.bom.line'].search(
            ['|', ('product_template', '=', self.product_template.id),
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
            lambda x: x.product_id == product)
        line.write({'product_qty': qty})

    @api.one
    def assign_parent_lot(self, production):
        line = self.product_lines.filtered(
            lambda x: x.product_id == production.product_id)
        line.write({'lot': (
                    production.move_created_ids2 and
                    production.move_created_ids2[0].restrict_lot_id.id or
                    False)})

    @api.one
    def create_mo_from_packaging_operation(self):
        for op in self.pack.filtered(lambda x: x.qty != 0 and not x.processed):
            linked_raw_products = []
            add_product = []
            equal_uom = op.product.uom_id.id == self.product_id.uom_id.id
            final_product_qty = equal_uom and op.fill or op.qty
            data = self.product_id_change(op.product.id, final_product_qty)
            if 'product_attributes' in data['value']:
                product_attributes = map(
                    lambda x: (0, 0, x),
                    data['value']['product_attributes'])
                data['value'].update({
                    'product_attributes': product_attributes})
            name = self.env['ir.sequence'].get('mrp.production.packaging')
            data['value'].update({
                'product_id': op.product.id,
                'product_qty': final_product_qty,
                'name': name})
            new_op = self.create(data['value'])
            new_op.action_compute()
            new_op.recalculate_product_qty(op.fill, self.product_id)
            new_op.assign_parent_lot(self)
            workorder =\
                new_op.workcenter_lines and new_op.workcenter_lines[0].id
            for attr_value in op.product.attribute_value_ids:
                raw_product = attr_value.raw_product
                if raw_product:
                    value = self.get_new_components_info(
                        raw_product.id,
                        raw_product.property_stock_production.id,
                        raw_product.property_stock_inventory.id,
                        raw_product.uom_id.id,
                        raw_product.uos_id.id,
                        op.qty, workorder)
                    linked_raw_products.append(value)
            for line in new_op.product_lines:
                if self.product_id.product_tmpl_id == line.product_template:
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
        else:
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
