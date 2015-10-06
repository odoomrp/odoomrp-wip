# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api, _


class MrpBomSaleOrder(models.Model):
    _name = 'mrp.bom.sale.order'

    bom_line = fields.Many2one(comodel_name='mrp.bom.line')
    product_id = fields.Many2one(related='bom_line.product_id',
                                 string='Product')
    product_uom = fields.Many2one(related='bom_line.product_uom',
                                  string='Unit of Measure ')
    product_uom_qty = fields.Float(string='Quantity (UoS)')
    sale_order = fields.Many2one(comodel_name='sale.order.line')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    mrp_boms = fields.One2many(comodel_name='mrp.bom.sale.order',
                               inverse_name='sale_order', string='Mrp BoM',
                               copy=True)

    @api.one
    @api.depends('product_uom_qty', 'product_id')
    def _calc_stock(self):
        for line in self:
            v_stock = []
            r_stock = []
            for oline in line.mrp_boms:
                v_stock.append(oline.bom_line.product_id.virtual_available /
                               (oline.product_uom_qty))
                r_stock.append(oline.bom_line.product_id.qty_available /
                               (oline.product_uom_qty))
            line.virtual_stock = min(v_stock or [0])
            line.real_stock = min(r_stock or [0])

    virtual_stock = fields.Float(string='Virtual stock',
                                 compute='_calc_stock')
    real_stock = fields.Float(string='Stock', compute='_calc_stock')

    @api.multi
    def product_id_change(
            self, pricelist, product, qty=0, uom=False, qty_uos=0,
            uos=False, name='', partner_id=False, lang=False, update_tax=True,
            date_order=False, packaging=False, fiscal_position=False,
            flag=False):
        res = super(SaleOrderLine, self).product_id_change(
            pricelist, product, qty=qty, uom=uom, qty_uos=qty_uos, uos=uos,
            name=name, partner_id=partner_id, lang=lang, update_tax=update_tax,
            date_order=date_order, packaging=packaging,
            fiscal_position=fiscal_position, flag=flag)
        mrp_bom_obj = self.env['mrp.bom']
        product_obj = self.env['product.product']
        product_id = product_obj.search([('id', '=', product)])
        mrp_bom = []
        mrp_bom = mrp_bom_obj.search([
            ('product_tmpl_id', '=', product_id.product_tmpl_id.id),
            ('type', '=', 'phantom')])
        order_lines = []
        for line in mrp_bom.bom_line_ids:
            order_line = {
                'bom_line': line.id,
                'product_uom_qty':
                line.product_qty * qty,
            }
            order_lines.append(order_line)
        res['value'].update({'mrp_boms': ([(0, 0, oline)
                                           for oline in order_lines])})
        return res


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def _action_explode(self, move):
        res = super(StockMove, self)._action_explode(move)
        bom_obj = self.env['mrp.bom']
        product_obj = self.env['product.product']
        for new_move in self.env['stock.move'].browse(res):
            product = product_obj.search([(
                'id', '=', new_move.procurement_id.product_id.id)])
            if bom_obj.search([
                '&', ('product_tmpl_id', '=', product.product_tmpl_id.id),
                    ('type', '=', 'phantom')]):
                    new_move.note = (
                        _('Product: "%s" \n') % (new_move.procurement_id.name))
        return res

    @api.multi
    def _picking_assign(self, procurement_group, location_from,
                        location_to):
        res = super(StockMove, self)._picking_assign(
            procurement_group, location_from, location_to)
        pick_obj = self.env['stock.picking']
        notes = []
        for move in self:
            for procurement in move.procurement_id:
                if procurement not in notes and move.note:
                    notes.append(procurement)
                    picking = pick_obj.search(
                        [('id', '=', move.picking_id.id)])
                    picking.note = (picking.note or '') + move.note
        return res
