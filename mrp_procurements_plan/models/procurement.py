# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    level = fields.Integer(string='Level')

    @api.multi
    def make_mo(self):
        production_obj = self.env['mrp.production']
        result = super(ProcurementOrder, self).make_mo()
        procurement = self.browse(result.keys()[0])
        production = production_obj.browse(result.values()[0])
        if procurement.plan:
            production.write({'plan': procurement.plan.id})
        return result

    @api.multi
    def set_main_plan(self):
        procurement_obj = self.env['procurement.order']
        for record in self:
            if record.production_id:
                production = record.production_id
                if production.plan:
                    moves = production.move_lines
                    for move in moves:
                        procurements = procurement_obj.search(
                            [('move_dest_id', '=', move.id)])
                        procurements.write({'plan': production.plan.id})
                        procurements.refresh()
                        procurements.set_main_plan()
                    if record.move_ids:
                        for move in record.move_ids:
                            procurements = procurement_obj.search(
                                [('move_dest_id', '=', move.id)])
                            procurements.write({'plan': production.plan.id})
                            procurements.refresh()
                            procurements.set_main_plan()
        return True

    @api.multi
    def run(self, autocommit=False):
        res = super(ProcurementOrder, self).run(autocommit=autocommit)
        self.set_main_plan()
        return res


class ProcurementPlan(models.Model):
    _inherit = 'procurement.plan'

    product_id = fields.Many2one(
        'product.product', string='Final Product')
    previous_product_id = fields.Many2one(
        'product.product', string='Previous Final Product')
    qty_to_produce = fields.Integer(
        string='Quantity to be produced')
    mrp_bom_id = fields.Many2one(
        'mrp.bom', string='MRP BoM')
    production_ids = fields.One2many(
        'mrp.production', 'plan', string='Productions', readonly=True)

    @api.one
    def action_import(self):
        if self.product_id:
            raise exceptions.Warning(_('Error!: You can not import'
                                       ' procurements, there is defined an'
                                       ' final product'))
        super(ProcurementPlan, self).action_import()

    @api.multi
    def button_generate_procurements(self):
        for plan in self:
            if not plan.product_id:
                raise exceptions.Warning(_('Error!: You must enter the final'
                                           ' product'))
            if not plan.qty_to_produce:
                raise exceptions.Warning(_('Error!: You must enter the'
                                           ' quantity to produce'))
            if not plan.mrp_bom_id:
                raise exceptions.Warning(_('Error!: No BoM found'))
            if len(plan.procurement_ids) > 0 and self.state != 'cancel':
                raise exceptions.Warning(_('Error!: Already generated'
                                           ' procurements orders'))
            for line in plan.mrp_bom_id.bom_line_ids:
                self._create_procurement_from_bom_line(
                    plan, 1, line.product_id, line.product_qty)
                if line.child_line_ids:
                    self._calculate_bom_line_details(
                        plan, line.child_line_ids, 1)
        return True

    def _calculate_bom_line_details(self, plan, child_line_ids, level):
        level += 1
        for line in child_line_ids:
            self._create_procurement_from_bom_line(
                plan, level, line.product_id, line.product_qty)
            if line.child_line_ids:
                self._calculate_bom_line_details(
                    plan, line.child_line_ids, level)
        return True

    def _create_procurement_from_bom_line(self, plan, level, product,
                                          product_qty):
        company_id = self.env['res.users']._get_company()
        cond = [('company_id', '=', company_id)]
        warehouse_ids = self.env['stock.warehouse'].search(cond)
        if not warehouse_ids:
            raise exceptions.Warning(_('Error!: Warehouse not found.'))
        procurement_obj = self.env['procurement.order']
        qty = ((product_qty * self.qty_to_produce) /
               self.mrp_bom_id.product_qty)
        vals = {'name': plan.name,
                'origin': plan.sequence,
                'level': level,
                'product_id': product.id,
                'plan': self.id,
                'main_project_id': self.project_id.id,
                'product_qty': qty,
                'warehouse_id': warehouse_ids[0].id,
                'location_id':  warehouse_ids[0].lot_stock_id.id
                }
        vals.update(procurement_obj.onchange_product_id(product.id)['value'])
        procurement = procurement_obj.create(vals)
        procurement.write({'rule_id': procurement_obj._find_suitable_rule(
            procurement)})
        return True

    @api.multi
    @api.onchange('product_id')
    def onchange_product_id(self):
        bom_obj = self.env['mrp.bom']
        if len(self.procurement_ids) and self.state != 'cancel':
            self.product_id = self.previous_product_id.id
            return {'warning': {
                    'title': _('Error!'),
                    'message': _("You can not change product")
                    }}
        self.previous_product_id = self.product_id.id
        self.mrp_bom_id = False
        if self.product_id:
            cond = ['|', ('product_tmpl_id', '=',
                    self.product_id.product_tmpl_id.id),
                    ('product_id', '=', self.product_id.id)]
            boms = bom_obj.search(cond)
            if not boms:
                self.product_id = False
                raise exceptions.Warning(_('Error!: No BoM found'))
            sorted_boms = sorted(boms, key=lambda l: l.sequence, reverse=True)
            self.mrp_bom_id = sorted_boms[0].id
        return {}
