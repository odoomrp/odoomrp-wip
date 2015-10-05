# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _
from dateutil.relativedelta import relativedelta


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.one
    def _compute_show_buttons(self):
        bom_obj = self.env['mrp.bom']
        self.show_button_create = False
        self.show_button_delete = False
        if (self.location_id.usage == 'internal' and
                self.state not in ('cancel', 'done')):
            cond = [('parent_procurement_id', '=', self.id)]
            child_procs = self.search(cond, limit=1)
            cond = ['|', ('product_tmpl_id', '=',
                    self.product_id.product_tmpl_id.id),
                    ('product_id', '=', self.product_id.id)]
            boms = bom_obj.search(cond)
            if child_procs:
                self.show_button_delete = bool(boms)
            else:
                self.show_button_create = bool(boms)

    level = fields.Integer(string='Level', default=0)
    parent_procurement_id = fields.Many2one(
        'procurement.order', string='Procurement Parent')
    show_button_create = fields.Boolean(
        string='Show button Create', compute='_compute_show_buttons')
    show_button_delete = fields.Boolean(
        string='Show button Delete', compute='_compute_show_buttons')

    @api.multi
    def make_mo(self):
        production_obj = self.env['mrp.production']
        result = super(ProcurementOrder, self).make_mo()
        procurement = self.browse(result.keys()[0])
        production = production_obj.browse(result[procurement.id])
        if procurement.plan:
            production.write({'plan': procurement.plan.id})
        return result

    @api.multi
    def button_erase_lower_levels(self):
        reservation_obj = self.env['stock.reservation']
        self.ensure_one()
        cond = [('parent_procurement_id', 'child_of', self.id),
                ('id', '!=', self.id)]
        procs = self.search(cond)
        cond = [('procurement_from_plan', 'in', procs.ids)]
        reservations = reservation_obj.search(cond)
        procs.cancel()
        procs.unlink()
        reservations.unlink()
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

    @api.one
    def _create_procurement_plan_from_procurement(self, sale):
        plan_obj = self.env['procurement.plan']
        project_obj = self.env['project.project']
        vals = {'name': _('Generated from sale order: ') + sale.name,
                'warehouse_id': self.warehouse_id.id,
                'from_date': self.date_planned,
                'to_date': self.date_planned,
                'procurement_ids': [(4, self.id)]}
        if sale.main_project_id:
            vals['project_id'] = sale.main_project_id.id
        else:
            project = project_obj.create({'name': sale.name})
            vals['project_id'] = project.id
        procurement_plan = plan_obj.create(vals)
        self._create_procurement_lower_levels(procurement_plan.id)
        for proc in procurement_plan.procurement_ids:
            if proc.show_button_create:
                proc.button_create_lower_levels()

    @api.one
    def _create_procurement_lower_levels(self, plan_id):
        plan_obj = self.env['procurement.plan']
        plan = plan_obj.browse(plan_id)
        procurements = plan.procurement_ids.filtered('show_button_create')
        while procurements:
            procurements.button_create_lower_levels()
            plan.refresh()
            procurements = plan.procurement_ids.filtered('show_button_create')


class ProcurementPlan(models.Model):
    _inherit = 'procurement.plan'

    production_ids = fields.One2many(
        'mrp.production', 'plan', string='Productions', readonly=True)

    @api.one
    def button_generate_mrp_procurements(self):
        cond = [('name', '=', 'Manufacture')]
        route = self.env['stock.location.route'].search(cond)
        for procurement in self.procurement_ids.filtered(
                lambda r: r.level == 0 and r.location_id.usage ==
                'internal' and route[0].id in r.product_id.route_ids.ids):
            cond = [('parent_procurement_id', '=', procurement.id)]
            child_procs = self.env['procurement.order'].search(cond, limit=1)
            if not child_procs:
                cond = ['|', ('product_tmpl_id', '=',
                        procurement.product_id.product_tmpl_id.id),
                        ('product_id', '=', procurement.product_id.id)]
                boms = self.env['mrp.bom'].search(cond)
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
        if not line.product_id:
            product_errors.append(
                {'error': (_('Product has not been found on the list of'
                             ' materials %s, Level %s') % (bom.name,
                                                           str(level)))})
        else:
            procurement = self._create_procurement_from_bom_line(
                level, line.product_id, qty, procurement)
            self._create_stock_reservation(procurement)
        for child in line.child_line_ids:
            if child.child_line_ids:
                self._calculate_bom_line_details(
                    child, child.product_qty * qty, level,
                    product_errors, procurement, bom)
            else:
                if not child.product_id:
                    raise exceptions.Warning(
                        _('No product defined for BoM line with template: %s,'
                          ' on the list of materials %s') %
                        (child.product_template.name, line.product_id.name))
                procurement = self._create_procurement_from_bom_line(
                    level+1, child.product_id, child.product_qty * qty,
                    procurement)
                self._create_stock_reservation(procurement)
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
        vals = {'name': self.name,
                'origin': self.sequence,
                'level': level,
                'product_id': product.id,
                'plan': self.id,
                'main_project_id': self.project_id.id,
                'product_qty': qty,
                'warehouse_id': self.warehouse_id.id,
                'location_id':  self.warehouse_id.lot_stock_id.id,
                'parent_procurement_id': (procurement.id or False)
                }
        if procurement:
            days_to_sum = 0
            for route in product.route_ids:
                if route.name == 'Manufacture':
                    days_to_sum = (product.produce_delay or 0)
                    break
                elif route.name == 'Buy':
                    suppliers = product.supplier_ids.filtered(
                        lambda x: x.type == 'supplier')
                    if suppliers:
                        sorted_suppliers = sorted(suppliers, reverse=True,
                                                  key=lambda l: l.sequence)
                        days_to_sum = (sorted_suppliers[0].delay or 0)
                    break
            date = (fields.Date.from_string(procurement.date_planned[0:10]) -
                    (relativedelta(days=days_to_sum)))
            vals['date_planned'] = date
        res = procurement_obj.onchange_product_id(product.id)
        vals.update('value' in res and res['value'] or {})
        return vals

    def _create_stock_reservation(self, procurement):
        reservation_obj = self.env['stock.reservation']
        dest_location_id = self.env.ref(
            'stock_reserve.stock_location_reservation').id
        vals = {'name': procurement.product_id.name,
                'product_id': procurement.product_id.id,
                'product_uom_qty': procurement.product_qty,
                'product_uom': procurement.product_uom.id,
                'company_id': procurement.company_id.id,
                'location_id': procurement.location_id.id,
                'dest_location_id': dest_location_id,
                'procurement_from_plan': procurement.id,
                'origin': self.sequence,
                'date_expected': procurement.date_planned
                }
        reservation_obj.create(vals)
