# -*- coding: utf-8 -*-
# (c) 2014 Daniel Campos - AvanzOSC
# (c) 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, exceptions, api, _


class ProductPricelistLoad(models.Model):
    _name = 'product.pricelist.load'
    _description = 'Product Price List Load'

    name = fields.Char('Load')
    date = fields.Date('Date:', readonly=True)
    file_name = fields.Char('File Name', readonly=True)
    file_lines = fields.One2many('product.pricelist.load.line', 'file_load',
                                 'Product Price List Lines')
    fails = fields.Integer('Fail Lines:', readonly=True)
    process = fields.Integer('Lines to Process:', readonly=True)
    supplier = fields.Many2one('res.partner')

    @api.multi
    def process_lines(self):
        for file_load in self:
            if not file_load.supplier:
                raise exceptions.Warning(_("You must select a Supplier"))
            product_obj = self.env['product.product']
            psupplinfo_obj = self.env['product.supplierinfo']
            pricepinfo_obj = self.env['pricelist.partnerinfo']
            if not file_load.file_lines:
                raise exceptions.Warning(_("There must be one line at least to"
                                           " process"))
            for line in file_load.mapped('file_lines').filtered(
                    lambda x: x.fail and (x.code or x.info)):
                cond = ([('default_code', '=', line.code)] if line.code else
                        [('name', '=', line.info)])
                product_lst = product_obj.search(cond, limit=1)
                if product_lst:
                    psupplinfo = product_lst.mapped('supplier_ids').filtered(
                        lambda x: x.name.id == file_load.supplier.id)
                    if not psupplinfo:
                        psupplinfo = psupplinfo_obj.create(
                            {'name': file_load.supplier.id,
                             'min_qty': 1,
                             'product_tmpl_id':
                             product_lst[0].product_tmpl_id.id})
                    if not psupplinfo.pricelist_ids:
                        pricepinfo_obj.create(
                            {'suppinfo_id': psupplinfo.id,
                             'min_quantity': psupplinfo.min_qty,
                             'price': line.price})
                        m = ("<p> " + str(fields.Datetime.now()) + ': ' +
                             _('New price: %s, has created for supplier: %s') %
                             (str(line.price), file_load.supplier.name))
                    else:
                        m = ("<p> " + str(fields.Datetime.now()) + ': ' +
                             _('Old price: %s, new price: %s, has modified for'
                               ' supplier: %s') %
                             (str(psupplinfo.pricelist_ids[0].price),
                              str(line.price), file_load.supplier.name))
                        psupplinfo.pricelist_ids[0].price = line.price
                    file_load.fails -= 1
                    line.write(
                        {'fail': False,
                         'fail_reason': _('Correctly Processed')})
                    m += "<br> <br>"
                    vals = {'type': 'comment',
                            'model': 'product.product',
                            'record_name': product_lst.name,
                            'res_id': product_lst.id,
                            'body': m}
                    self.env['mail.message'].create(vals)
                else:
                    line.fail_reason = _('Product not found')
        return True


class ProductPricelistLoadLine(models.Model):
    _name = 'product.pricelist.load.line'
    _description = 'Product Price List Load Line'

    code = fields.Char('Product Code')
    info = fields.Char('Product Description')
    price = fields.Float('Product Price', required=True)
    discount_1 = fields.Float('Product Discount 1')
    discount_2 = fields.Float('Product Discount 2')
    retail = fields.Float('Retail Price', required=True)
    pdv1 = fields.Float('PDV1')
    pdv2 = fields.Float('PDV2')
    fail = fields.Boolean('Fail')
    fail_reason = fields.Char('Fail Reason')
    file_load = fields.Many2one('product.pricelist.load', 'Load',
                                required=True)
