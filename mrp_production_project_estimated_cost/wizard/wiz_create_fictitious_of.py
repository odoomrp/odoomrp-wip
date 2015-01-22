# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _


class WizCreateFictitiousOf(models.TransientModel):
    _name = "wiz.create.fictitious.of"

    date_planned = fields.Datetime(
        string='Scheduled Date', required=True, default=fields.Datetime.now())

    @api.multi
    def do_create_fictitious_of(self):
        production_obj = self.env['mrp.production']
        product_obj = self.env['product.product']
        self.ensure_one()
        active_id = self._context['active_id']
        active_model = self._context['active_model']
        if active_model == 'product.template':
            cond = [('product_tmpl_id', '=', active_id)]
            product = product_obj.search(cond)
            if len(product) > 1:
                raise exceptions.Warning(
                    _('Error!: The product has variants'))
        else:
            product = product_obj.browse(active_id)
        vals = {'product_id': product.id,
                'product_qty': 1,
                'date_planned': self.date_planned,
                'user_id': self._uid,
                'location_src_id': production_obj._src_id_default(),
                'location_dest_id': production_obj._dest_id_default(),
                'active': False,
                'product_uom': product.uom_id.id
                }
        production_obj.create(vals)
        return True
