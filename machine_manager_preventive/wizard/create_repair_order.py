
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
            warehouse = self.env['ir.model.data'].get_object(
                'stock', 'warehouse0')
            return warehouse.lot_stock_id.id
        except:
            return False

    location_id = fields.Many2one('stock.location', 'Current Location',
                                  select=True, required=True,
                                  default=_default_stock_location)
    location_dest_id = fields.Many2one('stock.location', 'Delivery Location',
                                       select=True, required=True,
                                       default=_default_stock_location)

    @api.multi
    def create_order_from_pmo(self):
        value = {}
        prev_op_obj = self.env['preventive.machine.operation']
        rep_line_obj = self.env['mrp.repair.line']
        move_obj = self.env['stock.move']
        repair_obj = self.env['mrp.repair']
        multiple = False
        if len(self.env.context['active_ids']) > 1:
            multiple = True
            value = {
                'name': _('Create Order'),
                'view_type': 'form',
                'view_mode': 'tree, form',
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
                repair = repair_obj.create(
                    {'name': self.env['ir.sequence'].get('mrp.repair'),
                     'location_id': location_from.id,
                     'location_dest_id':  location_to.id,
                     'move_id': move.id,
                     'product_id': product.id,
                     'product_qty': 1,
                     'product_uom': product.product_tmpl_id.uom_id.id,
                     'preventive': True,
                     'idmachine': machine.id,
                     'prev_mach_op': [(6, 0, [op_pmo.id])],
                     'internal_notes': op_pmo.opdescription
                     })
            else:
                repair = repair_lst[0]
                repair.prev_mach_op = [op_pmo.id]
                if repair.internal_notes and op_pmo.opdescription:
                    repair.internal_notes = repair.internal_notes + (
                        '\n' + op_pmo.opdescription)
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
                    'state': 'draft', 'type': 'add',
                    'move_id': move.id,
                    'location_id': location_from.id,
                    'location_dest_id': location_to.id
                    })
            prev_op_obj.update_alerts(op_pmo)
            if not multiple:
                value = {
                    'name': _('Create Order'),
                    'view_type': 'form',
                    'view_mode': 'form,tree',
                    'res_model': 'mrp.repair',
                    'res_id': int(repair.id),
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    }
        return value
