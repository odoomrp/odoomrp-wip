# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.one
    def _compute_show_button_create(self):
        bom_obj = self.env['mrp.bom']
        self.show_button_create = False
        if self.location_id.usage == 'internal':
            cond = [('parent_procurement_id', '=', self.id)]
            child_procs = self.search(cond, limit=1)
            if not child_procs:
                cond = ['|', ('product_tmpl_id', '=',
                        self.product_id.product_tmpl_id.id),
                        ('product_id', '=', self.product_id.id)]
                boms = bom_obj.search(cond)
                if boms:
                    self.show_button_create = True

    @api.one
    def _compute_show_button_delete(self):
        bom_obj = self.env['mrp.bom']
        self.show_button_delete = False
        if self.location_id.usage == 'internal':
            cond = [('parent_procurement_id', '=', self.id)]
            child_procs = self.search(cond, limit=1)
            if child_procs:
                cond = ['|', ('product_tmpl_id', '=',
                        self.product_id.product_tmpl_id.id),
                        ('product_id', '=', self.product_id.id)]
                boms = bom_obj.search(cond)
                if boms:
                    self.show_button_delete = True

    level = fields.Integer(string='Level')
    parent_procurement_id = fields.Many2one(
        'procurement.order', string='Procurement Parent')
    show_button_create = fields.Boolean(
        string='Show button Create', compute='_compute_show_button_create')
    show_button_delete = fields.Boolean(
        string='Show button Delete', compute='_compute_show_button_delete')

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

    @api.multi
    def button_erase_lower_levels(self):
        self.ensure_one()
        cond = [('parent_procurement_id', 'child_of', self.id),
                ('id', '!=', self.id)]
        procs = self.search(cond)
        procs.cancel()
        procs.unlink()
        return {'view_type': 'form,tree',
                'view_mode': 'form',
                'res_model': 'procurement.plan',
                'res_id': self.plan.id,
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target': 'current',
                }

    @api.multi
    def button_create_lower_levels(self):
        bom_obj = self.env['mrp.bom']
        self.ensure_one()
        cond = ['|', ('product_tmpl_id', '=',
                self.product_id.product_tmpl_id.id),
                ('product_id', '=', self.product_id.id)]
        boms = bom_obj.search(cond)
        if not boms:
            message = (_('BoM not found, for product: %s') %
                       (self.product_id.name))
            message += "<br></p>"
            self.plan._create_message_error(message)
        else:
            product_errors = []
            sorted_boms = sorted(boms, key=lambda l: l.sequence,
                                 reverse=True)
            for line in sorted_boms[0].bom_line_ids:
                qty = ((line.product_qty * self.product_qty) /
                       sorted_boms[0].product_qty)
                product_errors = self.plan._calculate_bom_line_details(
                    line, qty, self.level, product_errors, self,
                    sorted_boms[0])
            if product_errors:
                message = ''
                for line_error in product_errors:
                    message += line_error['error'] + "<br>"
                message += "</p>"
                self.plan._create_message_error(message)
        return {'view_type': 'form,tree',
                'view_mode': 'form',
                'res_model': 'procurement.plan',
                'res_id': self.plan.id,
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target': 'current',
                }


class ProcurementPlan(models.Model):
    _name = 'procurement.plan'
    _inherit = ['procurement.plan', 'mail.thread']

    production_ids = fields.One2many(
        'mrp.production', 'plan', string='Productions', readonly=True)

    @api.multi
    def button_wizard_import(self):
        self.ensure_one()
        context = self.env.context.copy()
        context['active_id'] = self.id
        context['active_ids'] = [self.id]
        context['active_model'] = 'procurement.plan'
        return {'name': _('Import Procurements'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wiz.import.procurement.from.plan',
                'target': 'new',
                'context': context,
                }

    @api.one
    def button_generate_procurements(self):
        procurement_obj = self.env['procurement.order']
        bom_obj = self.env['mrp.bom']
        for procurement in self.procurement_ids.filtered(
                lambda r: r.level == 0 and r.location_id.usage == 'internal'):
            cond = [('parent_procurement_id', '=', procurement.id)]
            child_procs = procurement_obj.search(cond, limit=1)
            if not child_procs:
                cond = ['|', ('product_tmpl_id', '=',
                        procurement.product_id.product_tmpl_id.id),
                        ('product_id', '=', procurement.product_id.id)]
                boms = bom_obj.search(cond)
                if not boms:
                    message = (_('BoM not found, for product: %s') %
                               (procurement.product_id.name))
                    message += "<br></p>"
                    self._create_message_error(message)
                else:
                    product_errors = []
                    sorted_boms = sorted(boms, key=lambda l: l.sequence,
                                         reverse=True)
                    for line in sorted_boms[0].bom_line_ids:
                        qty = ((line.product_qty * procurement.product_qty) /
                               sorted_boms[0].product_qty)
                        product_errors = self._calculate_bom_line_details(
                            line, qty, 0, product_errors, procurement,
                            sorted_boms[0])
                    if product_errors:
                        message = ''
                        for line_error in product_errors:
                            message += line_error['error'] + "<br>"
                        message += "</p>"
                        self._create_message_error(message)
        self._catch_purchases()

    def _create_message_error(self, message):
        m = "<p> " + (str(fields.Datetime.now()) + ': ' +
                      _('THEY HAVE NOT GENERATED ALL PROCUREMENTS')) + "<br>"
        m += "<br> <br>"
        m += message
        vals = {'type': 'comment',
                'model': 'procurement.plan',
                'record_name': self.name,
                'res_id': self.id,
                'body': m}
        self.env['mail.message'].create(vals)

    def _calculate_bom_line_details(self, line, qty, level, product_errors,
                                    procurement, bom):
        level += 1
        if not line.product_id and not line.product_template:
            product_errors.append(
                {'error': (_('Product has not been found, or product template,'
                             ' on the list of materials %s, Level %s')
                           % (bom.name, str(level)))})
        elif not line.product_id and line.product_template:
            product_errors.append(
                {'error': (_('Product has not been found on the list of'
                             ' materials %s, product template %s, Level %s') %
                           (bom.name, line.product_template.name,
                            str(level)))})
        else:
            procurement = self._create_procurement_from_bom_line(
                level, line.product_id, qty, procurement)
        for child in line.child_line_ids:
            if child.child_line_ids:
                self._calculate_bom_line_details(
                    child, child.product_qty * qty, level,
                    product_errors, procurement, bom)
            else:
                procurement = self._create_procurement_from_bom_line(
                    level+1, child.product_id, child.product_qty * qty,
                    procurement)
        return product_errors

    def _create_procurement_from_bom_line(self, level, product, qty,
                                          procurement):
        procurement_obj = self.env['procurement.order']
        vals = self._prepare_procurements_vals(level, product, qty,
                                               procurement)
        proc = procurement_obj.create(vals)
        proc.write({'rule_id': procurement_obj._find_suitable_rule(proc)})
        return proc

    def _prepare_procurements_vals(self, level, product, qty, procurement):
        procurement_obj = self.env['procurement.order']
        warehouse_ids = self.env['stock.warehouse'].search([])
        if not warehouse_ids:
            raise exceptions.Warning(_('Error!: Warehouse not found.'))
        vals = {'name': self.name,
                'origin': self.sequence,
                'level': level,
                'product_id': product.id,
                'plan': self.id,
                'main_project_id': self.project_id.id,
                'product_qty': qty,
                'warehouse_id': warehouse_ids[0].id,
                'location_id':  warehouse_ids[0].lot_stock_id.id,
                'parent_procurement_id': (procurement.id or False)
                }
        vals.update(procurement_obj.onchange_product_id(product.id)['value'])
        return vals
