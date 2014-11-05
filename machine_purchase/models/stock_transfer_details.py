
from openerp import models, exceptions, api, _


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    @api.one
    def do_detailed_transfer(self):
        for lstits in [self.item_ids, self.packop_ids]:
            for prod in lstits:
                if prod.packop_id:
                    product = prod.packop_id.product_id
                    if (product.track_outgoing or product.track_all) and (
                            product.product_tmpl_id.machine_ok):
                        if prod.quantity != 1:
                            raise exceptions.Warning(
                                _("Traceable Machine type products must be "
                                  "transfered unitarily"))
        return super(StockTransferDetails, self).do_detailed_transfer()
