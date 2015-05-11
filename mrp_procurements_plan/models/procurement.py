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
    _name = 'procurement.plan'
    _inherit = ['procurement.plan', 'mail.thread']

    product_id = fields.Many2one(
        'product.product', string='Final Product')
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
        result = {}
        for plan in self:
            if not plan.product_id:
                raise exceptions.Warning(_('Error!: You must enter the final'
                                           ' product'))
            if not plan.qty_to_produce:
                raise exceptions.Warning(_('Error!: You must enter the'
                                           ' quantity to produce'))
            if not plan.mrp_bom_id:
                raise exceptions.Warning(_('Error!: No BoM found'))
            if plan.procurement_ids and self.state != 'cancel':
                raise exceptions.Warning(_('Error!: Already generated'
                                           ' procurements orders'))
            product_errors = []
            for line in plan.mrp_bom_id.bom_line_ids:
                qty = ((line.product_qty * self.qty_to_produce) /
                       self.mrp_bom_id.product_qty)
                product_errors = self._calculate_bom_line_details(
                    plan, line, qty, 0, product_errors)
            plan._catch_purchases()
            if product_errors:
                message = "<p>" + _('THEY HAVE NOT GENERATED ALL PROCUREMENTS')
                message += str(fields.Datetime.now())
                message += "<br> <br>"
                for line_error in product_errors:
                    message += line_error['error'] + "<br>"
                message += "</p>"
                vals = {'type': 'comment',
                        'model': 'procurement.plan',
                        'record_name': plan.name,
                        'res_id': plan.id,
                        # 'res_id': mail.id,
                        'body': message}
                self.env['mail.message'].create(vals)
        return result

    def _calculate_bom_line_details(self, plan, line, qty, level,
                                    product_errors):
        level += 1
        if not line.product_id and not line.product_template:
            product_errors.append(
                {'error': (_('Product has not been found, or product template,'
                             ' on the list of materials %s, Level %s')
                           % (plan.mrp_bom_id.name, str(level)))})
        elif not line.product_id and line.product_template:
            product_errors.append(
                {'error': (_('Product has not been found on the list of'
                             ' materials %s, product template %s, Level %s') %
                           (plan.mrp_bom_id.name, line.product_template.name,
                            str(level)))})
        else:
            self._create_procurement_from_bom_line(plan, level,
                                                   line.product_id, qty)
        for child in line.child_line_ids:
            if child.child_line_ids:
                self._calculate_bom_line_details(
                    plan, child, child.product_qty * qty, level,
                    product_errors)
            else:
                self._create_procurement_from_bom_line(
                    plan, level+1, line.product_id, child.product_qty * qty)
        return product_errors

    def _create_procurement_from_bom_line(self, plan, level, product, qty):
        procurement_obj = self.env['procurement.order']
        vals = self._prepare_procurements_vals(plan, level, product, qty)
        procurement = procurement_obj.create(vals)
        procurement.write({'rule_id': procurement_obj._find_suitable_rule(
            procurement)})
        return True

    def _prepare_procurements_vals(self, plan, level, product, qty):
        procurement_obj = self.env['procurement.order']
        warehouse_ids = self.env['stock.warehouse'].search([])
        if not warehouse_ids:
            raise exceptions.Warning(_('Error!: Warehouse not found.'))
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
        return vals

    @api.multi
    @api.onchange('product_id')
    def onchange_product_id(self):
        bom_obj = self.env['mrp.bom']
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
