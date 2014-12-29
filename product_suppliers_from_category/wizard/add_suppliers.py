
# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
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

from openerp import api, models, fields


class AddSuppliers(models.TransientModel):

    _name = 'add.suppliers'

    remove_others = fields.Boolean(
        string="Remove providers who are not in the category of the product")

    @api.one
    def assign_suppliers(self):
        new_supps = []
        prod_obj = self.env[self.env.context['active_model']]
        prod = prod_obj.browse(self.env.context.get('active_ids'))
        if self.remove_others:
            for supplier in prod.seller_ids:
                if supplier.name not in prod.categ_id.suppliers:
                    prod.write({'seller_ids': [(2, supplier.id)]})
        exist_supp = [x.name for x in prod.seller_ids]
        for supplier in prod.categ_id.suppliers:
            if supplier not in exist_supp:
                new_supps.append((0, 0, {'name': supplier.id}))
        prod.write({'seller_ids': new_supps})
