# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import api, models, fields


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def get_new_components_info(self, product_id, loc_id, loc_dest_id,
                                uom_id, uos_id, qty, workorder):
        move_obj = self.env['stock.move']
        ul_move = move_obj.onchange_product_id(
            prod_id=product_id,
            loc_id=loc_id,
            loc_dest_id=loc_dest_id)
        ul_move['value'].update({
            'product_id': product_id,
            'product_uom': uom_id,
            'product_uos': uos_id,
            'product_qty': qty,
            'work_order': workorder,
            'product_uos_qty': move_obj.onchange_quantity(
                product_id, qty, uom_id,
                uos_id)['value']['product_uos_qty']})
        return ul_move['value']

    def get_raw_products_data(self):
        res = []
        workorder =\
            self.workcenter_lines and self.workcenter_lines[0].id
        for attr_value in self.product_id.attribute_value_ids:
            raw_product = attr_value.raw_product
            if raw_product:
                bom_obj = self.env['mrp.bom']
                bom_id = bom_obj._bom_phantom_find(
                    product_id=raw_product.id)
                qty = self.product_qty * attr_value.raw_qty
                if not bom_id:
                    value = self.get_new_components_info(
                        raw_product.id,
                        raw_product.property_stock_production.id,
                        raw_product.property_stock_inventory.id,
                        raw_product.uom_id.id,
                        raw_product.uos_id.id,
                        qty,
                        workorder)
                    res.append(value)
                else:
                    result, result1 = bom_obj._bom_explode(
                        bom_obj.browse(bom_id), raw_product.id,
                        self.product_qty * attr_value.raw_qty)
                    for line in result:
                        product = self.env['product.product'].browse(
                            line['product_id'])
                        value = self.get_new_components_info(
                            line['product_id'],
                            product.property_stock_production.id,
                            product.property_stock_inventory.id,
                            product.uom_id.id,
                            product.uos_id.id,
                            line['product_qty'] * qty,
                            workorder)
                        res.append(value)
        return res

    @api.one
    def action_compute(self, properties=None):
        result = super(MrpProduction, self).action_compute(
            properties=properties)
        res = self.get_raw_products_data()
        self.write({'product_lines': map(lambda x: (0, 0, x), res)})
        return result

    product_id = fields.Many2one()
    raw_products = fields.One2many('mrp.production.product.line',
                                   'raw_production', string='Raw Products')

    @api.one
    @api.onchange('product_id')
    def onchange_bring_raw_products(self):
        self.raw_products = self.get_raw_products_data()


class MrpProductionProductLine(models.Model):
    _inherit = 'mrp.production.product.line'

    raw_production = fields.Many2one('mrp.production', string='Production')


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    def _bom_phantom_find(
            self, product_tmpl_id=None, product_id=None, properties=None):
        """ Finds BoM for particular product and product uom.
        @param product_tmpl_id: Selected product.
        @param product_uom: Unit of measure of a product.
        @param properties: List of related properties.
        @return: False or BoM id.
        """
        if properties is None:
            properties = []
        if product_id:
            if not product_tmpl_id:
                product_tmpl_id = self.env['product.product'].browse(
                    product_id).product_tmpl_id.id
            domain = [
                '|', ('product_id', '=', product_id),
                '&', ('product_id', '=', False),
                ('product_tmpl_id', '=', product_tmpl_id)
            ]
        elif product_tmpl_id:
            domain = [('product_id', '=', False),
                      ('product_tmpl_id', '=', product_tmpl_id)]
        else:
            # neither product nor template, makes no sense to search
            return False
        domain += [('type', '=', 'phantom')]
        domain = domain + ['|', ('date_start', '=', False),
                           ('date_start', '<=', fields.Datetime.now()),
                           '|', ('date_stop', '=', False),
                           ('date_stop', '>=', fields.Datetime.now())]
        # order to prioritize bom with product_id over the one without
        bom_ids = self.search(domain, order='sequence, product_id')
        # Search a BoM which has all properties specified, or if you can not
        # find one, you could pass a BoM without any properties with the
        # smallest sequence
        bom_empty_prop = False
        for bom in bom_ids:
            if not (set(map(int, bom.property_ids or [])) -
                    set(properties or [])):
                if not properties or bom.property_ids:
                    return bom.id
                elif not bom_empty_prop:
                    bom_empty_prop = bom.id
        return bom_empty_prop
