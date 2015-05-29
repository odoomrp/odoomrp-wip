
# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields, api, exceptions, _


class PreventiveRepairOrder(models.TransientModel):
    """Create machine Preventive operations """
    _name = 'preventive.repair.order'
    _description = 'Create machine Preventive repair order'

    def _default_stock_location(self):
        try:
            warehouse = self.env['stock.warehouse'].search([], limit=1)
            return warehouse.lot_stock_id.id
        except:
            return False

    location_id = fields.Many2one('stock.location', 'Current Location',
                                  select=True, required=True,
                                  default=_default_stock_location)
    location_dest_id = fields.Many2one('stock.location', 'Delivery Location',
                                       select=True, required=True,
                                       default=_default_stock_location)
    invoice_method = fields.Selection([
        ("none", "No Invoice"), ("b4repair", "Before Repair"),
        ("after_repair", "After Repair")], "Invoice Method", select=True,
        default='none')
    partner = fields.Many2one('res.partner', 'Partner', select=True,
                              help='Choose partner for whom the order will be '
                              'invoiced and delivered.')
    invoice_address = fields.Many2one(
        'res.partner', 'Invoicing Address',
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
                      'partner_invoice_id': inv_address_id
                      }
        return order_vals

    @api.multi
    def create_order_from_pmo(self):
        prev_op_obj = self.env['preventive.machine.operation']
        rep_line_obj = self.env['mrp.repair.line']
        move_obj = self.env['stock.move']
        repair_obj = self.env['mrp.repair']
        multiple = False
        if len(self.env.context['active_ids']) > 1:
            multiple = True
        repair_order_lst = []
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
                    raise exceptions.Warning(
                        _('There is no product defined for machine: %s') %
                        op_pmo.machine.name)
                else:
                    raise exceptions.Warning(
                        _('There is no product defined for current machine'))
            product = machine.product
            location_from = self.location_id
            location_to = self.location_dest_id
            move = move_obj.create({
                'product_id': product.id,
                'name': product.name,
                'location_id': location_from.id,
                'location_dest_id': location_to.id,
                'product_uom': product.product_tmpl_id.uom_id.id,
                })
            repair_lst = repair_obj.search(
                [('product_id', '=', machine.product.id),
                 ('state', 'in', ('draft', 'confirmed', 'ready'))])
            if not repair_lst:
                repair_values = self._prepare_repair_order(
                    product, move, location_from, location_to, self.partner.id,
                    self.invoice_address.id, self.invoice_method, machine,
                    [op_pmo.id], op_pmo.opdescription)
                repair = repair_obj.create(repair_values)
            else:
                repair = repair_lst[0]
                repair.preventive_operations = [op_pmo.id]
                if repair.internal_notes and op_pmo.opdescription:
                    repair.internal_notes = repair.internal_notes + (
                        '\n' + op_pmo.opdescription)
                elif op_pmo.opdescription:
                    repair.internal_notes = op_pmo.opdescription
            if repair.id not in repair_order_lst:
                repair_order_lst.append(repair.id)
            for material in op_pmo.opname_omm.material:
                rep_line_obj.create({
                    'repair_id': repair.id,
                    'name': material.product_id.name,
                    'product_id': material.product_id.id,
                    'price_unit': material.product_id.lst_price,
                    'product_uom_qty': material.product_uom.id,
                    'product_uom': material.product_uom.id,
                    'to_invoice': 0,
                    'state': 'draft', 'type': 'add',
                    'move_id': move.id,
                    'location_id': location_from.id,
                    'location_dest_id': location_to.id
                    })
            if op_pmo.cycles:
                op_pmo.lastcycles = op_pmo.actcycles
            if op_pmo.interval_unit:
                op_pmo.lastdate = fields.Date.today()
            prev_op_obj.check_alerts()
        if not multiple:
            value['res_id'] = int(repair.id)
            value['view_mode'] = 'form,tree'
        else:
            value['domain'] = ("[('id','in',[" +
                               ','.join(map(str, repair_order_lst)) + "])]")
        return value
