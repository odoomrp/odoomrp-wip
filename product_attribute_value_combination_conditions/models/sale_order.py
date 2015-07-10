# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _
from openerp.addons import decimal_precision as dp


class ProductAttributeValueSaleLine(models.Model):
    _name = 'sale.order.line.attribute'

    @api.one
    @api.depends('value', 'sale_line.product_template')
    def _get_price_extra(self):
        price_extra = 0.0
        for price in self.value.price_ids:
            if price.product_tmpl_id.id == self.sale_line.product_template.id:
                price_extra = price.price_extra
        self.price_extra = price_extra

    @api.one
    @api.depends('attribute', 'sale_line.product_template',
                 'sale_line.product_template.attribute_line_ids')
    def _get_possible_attribute_values(self):
        attr_values = self.env['product.attribute.value']
        for attr_line in self.sale_line.product_template.attribute_line_ids:
            if attr_line.attribute_id.id == self.attribute.id:
                attr_values |= attr_line.value_ids
        self.possible_values = attr_values.sorted()

    @api.one
    def add_predecessor_attributes(self):
        attr_lines = self.sale_line.product_template.attribute_line_ids\
            .filtered(lambda x: self.attribute in x.predecessors)
        allowed_values = self.env['product.attribute.value']
        preserve_lines = self.env['sale.order.line.attribute']
        for line in attr_lines:
            allowed_values = line.value_constraints.filtered(
                lambda x: self.value in x.predecessor_values).mapped(
                'allowed_values')
            # for constraints in line.value_constraints:
            #     if self.value in constraints.predecessor_values:
            #         allowed_lines |= line
            #         allowed_values |= constraints.allowed_values
        for old_line in self.sale_line.product_attributes:
            if self != old_line:
                preserve_lines |= old_line
            else:
                preserve_lines |= old_line
                break
        unlink_lines = self.sale_line.product_attributes - preserve_lines
        unlink_lines and unlink_lines.unlink()
        for new_line in allowed_values.mapped('attribute_id'):
            self.sale_line.product_attributes |= \
                self.sale_line.product_attributes.new(
                    {'attribute': new_line.id,
                     'possible_values': allowed_values & new_line.value_ids})
        self.sale_line.refresh()

    sale_line = fields.Many2one(
        comodel_name='sale.order.line', string='Order line')
    # sale_line_copy = fields.Many2one(
    #     comodel_name='sale.order.line', string='Order line')
    attribute = fields.Many2one(
        comodel_name='product.attribute', string='Attribute')
    value = fields.Many2one(
        comodel_name='product.attribute.value', string='Value',
        domain="[('id', 'in', possible_values[0][2])]")
    possible_values = fields.Many2many(
        comodel_name='product.attribute.value',
        compute='_get_possible_attribute_values', readonly=True)
    price_extra = fields.Float(
        compute='_get_price_extra', string='Attribute Price Extra',
        digits=dp.get_precision('Product Price'),
        help="Price Extra: Extra price for the variant with this attribute"
        " value on sale price. eg. 200 price extra, 1000 + 200 = 1200.")
    sequence = fields.Integer(string="Sequence")


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_template = fields.Many2one(comodel_name='product.template',
                                       string='Product Template')
    product_attributes = fields.One2many(
        comodel_name='sale.order.line.attribute', inverse_name='sale_line',
        string='Product attributes', copy=True)
    # product_attributes_copy = fields.One2many(
    #     comodel_name='sale.order.line.attribute',
    #     inverse_name='sale_line_copy',
    #     string='Product attributes',
    #     computed="_calcule_predecessor_attributes")
    # Needed because one2many result type is not constant when evaluating
    # visibility in XML
    product_attributes_count = fields.Integer(
        compute="_get_product_attributes_count")
    order_state = fields.Selection(related='order_id.state', readonly=True)
    product_id = fields.Many2one(
        domain="[('product_tmpl_id', '=', product_template)]")

    @api.one
    @api.depends('product_attributes')
    def _get_product_attributes_count(self):
        self.product_attributes_count = len(self.product_attributes)
        # self.bring_predecessor_attributes()

    def _get_product_description(self, template, product, product_attributes):
        name = product and product.name or template.name
        group = self.env.ref(
            'product_attribute_value_combination_conditions.'
            'product_attribute_value_combination_conditions')
        extended = group in self.env.user.groups_id
        if not product_attributes and product:
            product_attributes = product.attribute_value_ids
        if extended:
            description = "\n".join(product_attributes.mapped(
                lambda x: "%s: %s" % (x.attribute_id.name, x.name)))
        else:
            description = ", ".join(product_attributes.mapped('name'))
        if not description:
            return name
        return ("%s\n%s" if extended else "%s (%s)") % (name, description)

    @api.multi
    def product_id_change(
            self, pricelist, product_id, qty=0, uom=False, qty_uos=0,
            uos=False, name='', partner_id=False, lang=False, update_tax=True,
            date_order=False, packaging=False, fiscal_position=False,
            flag=False):
        product_obj = self.env['product.product']
        res = super(SaleOrderLine, self).product_id_change(
            pricelist, product_id, qty=qty, uom=uom, qty_uos=qty_uos, uos=uos,
            name=name, partner_id=partner_id, lang=lang, update_tax=update_tax,
            date_order=date_order, packaging=packaging,
            fiscal_position=fiscal_position, flag=flag)
        if product_id:
            product = product_obj.browse(product_id)
            res['value']['product_attributes'] = (
                product._get_product_attributes_values_dict())
            res['value']['name'] = self._get_product_description(
                product.product_tmpl_id, product, product.attribute_value_ids)
        return res

    @api.multi
    @api.onchange('product_template')
    def onchange_product_template(self):
        self.ensure_one()
        self.name = self.product_template.name
        if not self.product_template.attribute_line_ids:
            self.product_id = (
                self.product_template.product_variant_ids and
                self.product_template.product_variant_ids[0])
        else:
            self.product_id = False
            self.product_uom = self.product_template.uom_id
            self.product_uos = self.product_template.uos_id
            self.price_unit = self.order_id.pricelist_id.with_context(
                {'uom': self.product_uom.id,
                 'date': self.order_id.date_order}).template_price_get(
                self.product_template.id, self.product_uom_qty or 1.0,
                self.order_id.partner_id.id)[self.order_id.pricelist_id.id]
        attribute_lines = self.product_template.attribute_line_ids.filtered(
            lambda x: x.initial is True)
        self.product_attributes = (
            attribute_lines.mapped(
                lambda x: {'attribute': x.attribute_id}))
        # Update taxes
        fpos = self.order_id.fiscal_position
        if not fpos:
            fpos = self.order_id.partner_id.property_account_position
        self.tax_id = fpos.map_tax(self.product_template.taxes_id)

    @api.one
    def add_predecessor_attributes(self):
        updated_lines = []
        pred_attr_values = self.env['product.attribute.value']
        allowed_values = self.env['product.attribute.value']
        for line in self.product_attributes:
            if line.attribute == \
                    self.product_template.attribute_line_ids.filtered(
                        lambda x: x.initial is True).mapped('attribute_id') \
                    or line.value in pred_attr_values:
                pred_attr_values = self.env['product.attribute.value']
                for attr_line in self.product_template.attribute_line_ids:
                    pred_attr_values |= attr_line.value_constraints.filtered(
                        lambda x: line.value in x.predecessor_values).mapped(
                        'allowed_values')
                updated_lines.append(
                    {'attribute': line.attribute.id,
                     'possible_values': pred_attr_values,
                     'value': line.value.id
                     })
            else:
                break
        for pred_attr in pred_attr_values.mapped('attribute_id'):
            allowed_values = pred_attr_values.filtered(
                lambda x: x.attribute_id == pred_attr)
            updated_lines.append({'attribute': pred_attr.id,
                                  'possible_values': allowed_values})
        self.product_attributes.unlink()
        self.product_attributes = updated_lines
        self.refresh()

    # def bring_predecessor_attributes(self):
    #     if not self.product_template:
    #         return
    #     attr_lines = self.product_template.attribute_line_ids\
    #         .filtered(lambda x: self.product_attributes[-1].attribute in
    #                             x.predecessors)
    #     allowed_lines = self.env['product.attribute.line']
    #     allowed_values = self.env['product.attribute.value']
    #     for line in attr_lines:
    #         for constraints in line.value_constraints:
    #             if self.product_attributes[-1].value in \
    #                     constraints.predecessor_values:
    #                 allowed_lines |= line
    #                 allowed_values |= constraints.allowed_values
    #     for old_line in self.product_attributes:
    #         if not old_line.value:
    #             old_line.unlink()
    #     for new_line in allowed_lines.mapped('attribute_id'):
    #         self.product_attributes |= self.product_attributes.new(
    #             {'attribute': new_line.id,
    #              'possible_values': allowed_values & new_line.value_ids
    #             })

    @api.one
    @api.onchange('product_attributes')
    def onchange_product_attributes(self):
        product_obj = self.env['product.product']
        # self.bring_predecessor_attributes()
        self.product_id = product_obj._product_find(
            self.product_template, self.product_attributes)
        if not self.product_id:
            self.name = self._get_product_description(
                self.product_template, False,
                self.product_attributes.mapped('value'))
        if self.product_template:
            self.update_price_unit()

    @api.multi
    def action_duplicate(self):
        self.ensure_one()
        self.copy()
        # Force reload of the view as a workaround for lp:1155525
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'sale.order',
            'res_id': self.order_id.id,
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def button_confirm(self):
        for line in self:
            if not line.product_id:
                product_obj = self.env['product.product']
                att_values_ids = [
                    attr_line.value and attr_line.value.id or False
                    for attr_line in line.product_attributes]
                domain = [('product_tmpl_id', '=', line.product_template.id)]
                for value in att_values_ids:
                    if not value:
                        raise exceptions.Warning(
                            _("You can not confirm before configuring all"
                              " attribute values."))
                    domain.append(('attribute_value_ids', '=', value))
                product = product_obj.search(domain)
                if not product:
                    product = product_obj.create(
                        {'product_tmpl_id': line.product_template.id,
                         'attribute_value_ids': [(6, 0, att_values_ids)]})
                line.write({'product_id': product.id})
        super(SaleOrderLine, self).button_confirm()

    @api.multi
    def update_price_unit(self):
        self.ensure_one()
        if not self.product_id:
            price_extra = 0.0
            for attr_line in self.product_attributes:
                price_extra += attr_line.price_extra
            self.price_unit = self.order_id.pricelist_id.with_context(
                {
                    'uom': self.product_uom.id,
                    'date': self.order_id.date_order,
                    'price_extra': price_extra,
                }).template_price_get(
                self.product_template.id, self.product_uom_qty or 1.0,
                self.order_id.partner_id.id)[self.order_id.pricelist_id.id]


    @api.cr_uid_ids_context
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
                          uom=False, qty_uos=0, uos=False, name='',
                          partner_id=False, lang=False, update_tax=True,
                          date_order=False, packaging=False, 
                          fiscal_position=False, flag=False, context=None):
        order = self.pool['sale.order'].browse(
            cr, uid, pricelist, context=context)
        return super(SaleOrderLine, self).product_id_change(
            cr, uid, ids, order.pricelist_id.id, product, qty=qty, uom=uom,
            qty_uos=qty_uos, uos=uos, name=name,
            partner_id=order.partner_id.id,
            lang=lang, update_tax=update_tax, date_order=order.date_order,
            packaging=packaging, fiscal_position=order.fiscal_position.id,
            flag=flag, context=context)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_act_window_dict(self, cr, uid, name, context=None):
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result = mod_obj.xmlid_to_res_id(cr, uid, name, raise_if_not_found=True)
        result = act_obj.read(cr, uid, [result], context=context)[0]
        return result


    @api.multi
    def action_open_lines(self):
        result = self._get_act_window_dict(
            'product_attribute_value_combination_conditions'
            '.act_sale_order_line')
        result['domain'] = "[('order_id', '=', " + str(self.id) + ")]"
        result['context'] = {'search_default_internal_loc': 1,
                             'search_default_order_id': self.id}
        result['target'] = 'current'
        return result