
from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        machinery_obj = self.env['machinery']
        purchase_obj = self.env['purchase.order']
        for invoice in self:
            if invoice.invoice_line and invoice.type == 'in_invoice':
                purchase_lst = purchase_obj.search(
                    [('invoice_method', '=', 'picking'), ('invoice_ids', '=',
                                                          invoice.id)])
                operation_ids = []
                if purchase_lst:
                    for purchase in purchase_lst:
                        for picking in purchase.picking_ids:
                            if picking.pack_operation_ids:
                                operation_ids.extend(
                                    picking.pack_operation_ids)
                # clean machine assigned operations
                if operation_ids:
                    for operation in operation_ids:
                        if operation.machine or operation.product_qty > 1:
                            operation_ids.remove(operation)
                for inv_line in invoice.invoice_line:
                    if inv_line.product_id.product_tmpl_id.machine_ok:
                        purchase_date = (invoice.date_invoice or
                                         fields.Date.today())
                        for x in range(0, int(inv_line.quantity)):
                            vals = {'name': inv_line.product_id.name,
                                    'product': inv_line.product_id.id,
                                    'purch_inv': invoice.id,
                                    'purch_partner': invoice.partner_id.id,
                                    'purch_date': purchase_date,
                                    'purch_cost': inv_line.price_unit,
                                    'purch_inv_line': inv_line.id
                                    }
                            machine = machinery_obj.create(vals)
                            for operation in operation_ids:
                                if machine.product == operation.product_id:
                                    operation.machine = machine
                                    machine.serial = operation.lot_id
                                    operation_ids.remove(operation)
                                    break
        return res
