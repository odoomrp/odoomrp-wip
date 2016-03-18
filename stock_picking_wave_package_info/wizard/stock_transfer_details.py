# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api
from datetime import datetime


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    @api.one
    def do_save_for_later(self):
        operation_obj = self.env['stock.pack.operation']
        for picking in self.picking_ids:
            # Create new and update existing pack operations
            picking.pack_operation_ids.unlink()
            for line in [self.item_ids.filtered(lambda x: x.picking_id.id ==
                                                picking.id),
                         self.packop_ids.filtered(lambda x: x.picking_id.id ==
                                                  picking.id)]:
                for prod in line:
                    pack_datas = {
                        'product_id': prod.product_id.id,
                        'product_uom_id': prod.product_uom_id.id,
                        'product_qty': prod.quantity,
                        'package_id': prod.package_id.id,
                        'lot_id': prod.lot_id.id,
                        'location_id': prod.sourceloc_id.id,
                        'location_dest_id': prod.destinationloc_id.id,
                        'result_package_id': prod.result_package_id.id,
                        'date': prod.date if prod.date else datetime.now(),
                        'owner_id': prod.owner_id.id,
                    }
                    if prod.packop_id:
                        prod.packop_id.with_context(no_recompute=True).write(
                            pack_datas)
                    else:
                        pack_datas['picking_id'] = picking.id
                        operation_obj.create(pack_datas)
        return True
