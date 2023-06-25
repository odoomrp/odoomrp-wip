# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP Module
#
#    Copyright (C) 2014 Asphalt Zipper, Inc.
#    Author scosist
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

import time
from openerp import models, api
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import ValidationError
from openerp.tools.translate import _


class mrp_bom(models.Model):
    _inherit = ['mrp.bom']

    @api.model
    def _bom_explode_llc(self, bom, product, result=None, properties=None,
                         llc=1, previous_products=None, master_bom=None):
        master_bom = master_bom or bom
        result = result or {}

        for bom_line_id in bom.bom_line_ids:
            if (bom_line_id.date_start and bom_line_id.date_start >
                time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)) or (
                    bom_line_id.date_stop and bom_line_id.date_stop <
                    time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)):
                continue
            # all bom_line_id variant values must be in the product
            if bom_line_id.attribute_value_ids:
                if not product or (
                    set(map(int, bom_line_id.attribute_value_ids or [])) - set(
                        map(int, product.attribute_value_ids))):
                    continue

            if (
                previous_products and
                bom_line_id.product_id.product_tmpl_id.id in
                previous_products
            ):
                raise ValidationError(
                    _('Invalid Action!'),
                    _('Bom "%s" contains a BoM line with a product'
                      ' recursion: "%s".'
                      ) % (master_bom.name,
                           bom_line_id.product_id.name_get()[0][1]))

            bom_id = self._bom_find(product_id=bom_line_id.product_id.id,
                                    properties=properties)

            if bom_id:
                all_prod = [bom.product_tmpl_id.id] + (previous_products or [])
                bom2 = self.browse(bom_id)
                if bom_line_id.type != "phantom" and bom2.type != "phantom":
                    if result[bom_line_id.product_id.id] < llc:
                        result[bom_line_id.product_id.id] = llc
                    res = self._bom_explode_llc(bom2, bom_line_id.product_id,
                                                result, properties, llc + 1,
                                                all_prod, master_bom)
                    result.update(res)
                else:
                    res = self._bom_explode_llc(bom2, bom_line_id.product_id,
                                                result, properties, llc,
                                                all_prod, master_bom)
                    result.update(res)
            elif bom_line_id.type != "phantom":
                if result[bom_line_id.product_id.id] < llc:
                    result[bom_line_id.product_id.id] = llc
            else:
                raise ValidationError(
                    _('Invalid Action!'),
                    _('BoM "%s" contains a phantom BoM line but the product'
                      ' "%s" does not have any BoM defined.'
                      ) % (master_bom.name,
                           bom_line_id.product_id.name_get()[0][1]))
        return result

    @api.model
    def _top_level_boms(self):
        bom_line_product_ids = []
        top_level_boms = set()
        bom_ids = self.search([])
        bom_line_obj = self.env['mrp.bom.line']
        bom_line_ids = bom_line_obj.search([])
        for bom_line in bom_line_ids:
            bom_line_product_ids.append(bom_line.product_id.id)
        for bom in bom_ids:
            bom_product_ids = []
            if bom.product_id:
                bom_product_ids.append(bom.product_id.id)
            else:
                for variant in bom.product_tmpl_id.product_variant_ids:
                    bom_product_ids.append(variant.id)
            # if any variants are in bom_line, do not add bom
            if not set(bom_product_ids).intersection(bom_line_product_ids):
                top_level_boms.add(bom.id)
        return top_level_boms

    @api.model
    def compute_llc(self, properties=None):
        llc_updates = {}
        # reset low level code first, then compute
        product_obj = self.env['product.product']
        product_ids = product_obj.search([])
        for product in product_ids:
            llc_updates[product.id] = 0
        top_level_boms = self._top_level_boms()
        for bom_point in self.browse(top_level_boms):
            res = self._bom_explode_llc(bom_point, bom_point.product_id,
                                        llc_updates, properties)
            for (key, val) in res.items():
                if val > llc_updates[key]:
                    llc_updates[key] = val
        for (key, val) in llc_updates.items():
            product_obj.browse([key]).write({'low_level_code': val})


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
