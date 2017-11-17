# -*- coding: utf-8 -*-
# Copyright 2016 Daniel Campos - Avanzosc S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _


class PreventiveRepairOrder(models.TransientModel):
    """Create machine Preventive operations """
    _name = 'preventive.repair.order'
    _description = 'Create machine Preventive repair order'

    def _default_stock_location(self):
        try:
            warehouse = self.env['stock.warehouse'].search([], limit=1)
            return warehouse.lot_stock_id.id
        except Exception:
            return False

    location_id = fields.Many2one(
        comodel_name='stock.location', string='Current Location', select=True,
        required=True, default=_default_stock_location)
    location_dest_id = fields.Many2one(
        comodel_name='stock.location', string='Delivery Location', select=True,
        required=True, default=_default_stock_location)
    invoice_method = fields.Selection(
        selection=[("none", "No Invoice"), ("b4repair", "Before Repair"),
                   ("after_repair", "After Repair")], string="Invoice Method",
        select=True, default='none')
    partner = fields.Many2one(
        comodel_name='res.partner', string='Partner', select=True,
        help="Choose partner for whom the order will be invoiced and "
        "delivered.")
    invoice_address = fields.Many2one(
        comodel_name='res.partner', string='Invoicing Address',
        domain="['|',('parent_id','=',partner),('id','=',partner)]")

    def _prepare_repair_order(self, product, move, location_from, location_to,
                              partner_id, inv_address_id, invoice_method,
                              machine, operation_lst, description):
        order_vals = {'name': self.env['ir.sequence'].get('mrp.repair'),
                      'location_id': location_from.id,
                      'location_dest_id':  location_to.id,
                      'move_id': move.id,
                      'product_id': product.id,
                      'product_qty': 1,
                      'product_uom': product.product_tmpl_id.uom_id.id,
                      'preventive': True,
                      'idmachine': machine.id,
                      'preventive_operations': [(6, 0, operation_lst)],
                      'internal_notes': description,
                      'invoice_method': invoice_method,
                      'partner_id': partner_id,
                      'partner_invoice_id': inv_address_id,
                      'lot_id': machine.serial.id,
                      }
        return order_vals

    @api.multi
    def create_repair_from_pmo(self):
        prev_op_obj = self.env['preventive.machine.operation']
        rep_line_obj = self.env['mrp.repair.line']
        move_obj = self.env['stock.move']
        repairs = repair_obj = self.env['mrp.repair']
        multiple = False
        if len(self.env.context['active_ids']) > 1:
            multiple = True
        value = {
            'name': _('Create Order'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'mrp.repair',
            'type': 'ir.actions.act_window',
            }
        for op_pmo_id in self.env.context['active_ids']:
            op_pmo = prev_op_obj.browse(op_pmo_id)
            machine = op_pmo.machine
            if not machine.product:
                if multiple:
                    raise exceptions.Warning(u"{}{}".format(
                        _('There is no product defined for machine: '),
                        op_pmo.machine.name))
                else:
                    raise exceptions.Warning(
                        _('There is no product defined for current machine'))
            product = machine.product
            condition = [('idmachine', '=', machine.id),
                         ('state', 'in', ('draft', 'confirmed', 'ready'))]
            if machine.serial:
                condition += [('lot_id', '=', machine.serial.id)]
            repair_lst = repair_obj.search(condition)
            if not repair_lst:
                location_from = self.location_id
                location_to = self.location_dest_id
                move = move_obj.create({
                    'product_id': product.id,
                    'name': product.name,
                    'location_id': location_from.id,
                    'location_dest_id': location_to.id,
                    'product_uom': product.product_tmpl_id.uom_id.id,
                    })
                repair_values = self._prepare_repair_order(
                    product, move, location_from, location_to, self.partner.id,
                    self.invoice_address.id, self.invoice_method, machine,
                    [op_pmo.id], op_pmo.opdescription)
                repair = repair_obj.create(repair_values)
                repairs += repair
            else:
                repair = repair_lst[0]
                repairs += repair
                if not repair.preventive:
                    repair.preventive = True
                repair.preventive_operations = [op_pmo.id]
                if repair.internal_notes and op_pmo.opdescription:
                    repair.internal_notes = u"{}\n{}".format(
                        repair.internal_notes, op_pmo.opdescription)
                elif op_pmo.opdescription:
                    repair.internal_notes = op_pmo.opdescription
            for material in op_pmo.opname_omm.material:
                rep_line_obj.create({
                    'repair_id': repair.id,
                    'name': material.product_id.name,
                    'product_id': material.product_id.id,
                    'price_unit': material.product_id.lst_price,
                    'product_uom_qty': material.product_uom.id,
                    'product_uom': material.product_uom.id,
                    'to_invoice': 0,
                    'state': 'draft',
                    'type': 'add',
                    'location_id': repair.location_id.id,
                    'location_dest_id': repair.location_dest_id.id,
                    })
            if op_pmo.update_preventive == 'before_repair':
                op_pmo._next_action_update()
        if not multiple:
            value['res_id'] = int(repair.id)
            value['view_mode'] = 'form,tree'
        else:
            value['domain'] = [('id', 'in', repairs.ids)]
        return value
