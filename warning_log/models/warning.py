
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
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

from openerp.osv import orm, fields
from datetime import datetime


class WarningLog(orm.Model):
    _name = "warning.log"
    _rec_name = 'user'
    _columns = {
        "date": fields.datetime("Date"),
        "user": fields.many2one("res.users", "User"),
        "msg": fields.text("Message"),
        "type": fields.many2one("ir.model", "Model")}

    def name_search(self, cr, uid, name='', args=None, operator='ilike',
                    context=None, limit=100):
        if not args:
            args = []
        ids = self.search(cr, uid, [('user', operator, name)] + args,
                          limit=limit, context=context)
        ids += self.search(cr, uid, [('date', operator, name)] + args,
                           limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = [(r.user.login, r.date)
               for r in self.browse(cr, uid, ids, context=context)]
        return res

    def create_warning_log(self, cr, uid, ids, model, warning,
                           context=None):
        if warning:
            model_id = self.pool['ir.model'].search(
                cr, uid, [('model', '=', model)], context=context)
            self.create(
                cr, uid, {
                    'date': datetime.now(), 'user': uid,
                    'msg': warning.get('message'),
                    'type': model_id[0]}, context=context)


class SaleOrder(orm.Model):

    _inherit = "sale.order"

    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        vals = super(SaleOrder, self).onchange_partner_id(cr, uid, ids, part,
                                                          context=context)
        self.pool['warning.log'].create_warning_log(
            cr, uid, ids, self._name, vals.get('warning'), context=context)
        return vals


class PurchaseOrder(orm.Model):
    _inherit = 'purchase.order'

    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        vals = super(PurchaseOrder, self).onchange_partner_id(
            cr, uid, ids, part, context=context)
        self.pool['warning.log'].create_warning_log(
            cr, uid, ids, self._name, vals.get('warning'), context=context)
        return vals


class AccountInvoice(orm.Model):
    _inherit = 'account.invoice'

    def onchange_partner_id(self, cr, uid, ids, invoice_type, partner_id,
                            date_invoice=False, payment_term=False,
                            partner_bank_id=False, company_id=False,
                            context=None):
        vals = super(AccountInvoice, self).onchange_partner_id(
            cr, uid, ids, invoice_type, partner_id, date_invoice=date_invoice,
            payment_term=payment_term, partner_bank_id=partner_bank_id,
            company_id=company_id, context=context)
        self.pool['warning.log'].create_warning_log(
            cr, uid, ids, self._name, vals.get('warning'), context=context)
        return vals


class StockPicking(orm.Model):
    _inherit = 'stock.picking'

    def onchange_partner_in(self, cr, uid, ids, partner_id=None,
                            context=None):
        vals = super(StockPicking, self).onchange_partner_in(
            cr, uid, ids, partner_id=partner_id, context=context)
        self.pool['warning.log'].create_warning_log(
            cr, uid, ids, self._name, vals.get('warning'), context=context)
        return vals


class SaleOrderLine(orm.Model):
    _inherit = 'sale.order.line'

    def product_id_change_with_wh(self, cr, uid, ids, pricelist, product,
                                  qty=0, uom=False, qty_uos=0, uos=False,
                                  name='', partner_id=False, lang=False,
                                  update_tax=True, date_order=False,
                                  packaging=False, fiscal_position=False,
                                  flag=False, warehouse_id=False,
                                  context=None):
        vals = super(SaleOrderLine, self).product_id_change_with_wh(
            cr, uid, ids, pricelist, product, qty=qty, uom=uom,
            qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order,
            packaging=packaging, fiscal_position=fiscal_position, flag=flag,
            warehouse_id=warehouse_id, context=context)
        self.pool['warning.log'].create_warning_log(
            cr, uid, ids, self._name, vals.get('warning'), context=context)
        return vals


class PurchaseOrderLine(orm.Model):
    _inherit = 'purchase.order.line'

    def onchange_product_id(
            self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False,
            date_planned=False, name=False, price_unit=False, state='draft',
            context=None):
        vals = super(PurchaseOrderLine, self).onchange_product_id(
            cr, uid, ids, pricelist_id, product_id, qty, uom_id, partner_id,
            date_order=date_order, fiscal_position_id=fiscal_position_id,
            date_planned=date_planned, name=name, price_unit=price_unit,
            state=state, context=context)
        self.pool['warning.log'].create_warning_log(
            cr, uid, ids, self._name, vals.get('warning'), context=context)
        return vals
