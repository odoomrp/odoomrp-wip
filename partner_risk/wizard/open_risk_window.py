
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009 Albert Cervera i Areny (http://www.nan-tic.com).
#    All Rights Reserved
#    Copyright (c) 2011 Pexego Sistemas Informáticos. All Rights Reserved
#                       Alberto Luengo Cabanillas <alberto@pexego.es>
#    Copyright (c) 2014 Factor Libre SL. All Rights Reserved
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
""" Open Risk Window and show Partner relative information """

from openerp.osv import orm, fields


class OpenRiskWindow(orm.TransientModel):
    """ Open Risk Window and show Partner relative information """
    _name = "open.risk.window"
    _description = "Partner's risk information"

    _columns = {
        'unpayed_amount': fields.float('Expired Unpaid Payments',
                                       digits=(4, 2), readonly="True"),
        'pending_amount': fields.float('Unexpired Unpaid Payments',
                                       digits=(4, 2), readonly="True"),
        'draft_invoices_amount': fields.float('Draft Invoices',
                                              digits=(4, 2), readonly="True"),
        'circulating_amount': fields.float('Payments Sent to Bank',
                                           digits=(4, 2), readonly="True"),
        'pending_orders_amount': fields.float('Uninvoiced Orders',
                                              digits=(4, 2), readonly="True"),
        'total_debt': fields.float('Total Debt', digits=(4, 2),
                                   readonly="True"),
        'credit_limit': fields.float('Credit Limit', digits=(4, 2),
                                     readonly="True"),
        'available_risk': fields.float('Available Credit', digits=(4, 2),
                                       readonly="True"),
        'total_risk_percent': fields.float('Credit Usage (%)', digits=(4, 2),
                                           readonly="True"),
        }
    _defaults = {
        'unpayed_amount': lambda self, cr, uid,
        context: self.pool['res.partner'].browse(
            cr, uid, context['active_id'], context).unpayed_amount or 0.0,
        'pending_amount': lambda self, cr, uid,
        context: self.pool['res.partner'].browse(
            cr, uid, context['active_id'], context).pending_amount or 0.0,
        'draft_invoices_amount': lambda self, cr, uid,
        context: self.pool['res.partner'].browse(
            cr, uid, context['active_id'],
            context).draft_invoices_amount or 0.0,
        'circulating_amount': lambda self, cr, uid,
        context: self.pool['res.partner'].browse(
            cr, uid, context['active_id'], context).circulating_amount or 0.0,
        'pending_orders_amount': lambda self, cr, uid,
        context: self.pool['res.partner'].browse(
            cr, uid, context['active_id'],
            context).pending_orders_amount or 0.0,
        'total_debt': lambda self, cr, uid,
        context: self.pool['res.partner'].browse(
            cr, uid, context['active_id'], context).total_debt or 0.0,
        'credit_limit': lambda self, cr, uid,
        context: self.pool['res.partner'].browse(
            cr, uid, context['active_id'], context).credit_limit or 0.0,
        'available_risk': lambda self, cr, uid,
        context: self.pool['res.partner'].browse(
            cr, uid, context['active_id'], context).available_risk or 0.0,
        'total_risk_percent': lambda self, cr, uid,
        context: self.pool['res.partner'].browse(
            cr, uid, context['active_id'], context).total_risk_percent or 0.0,
    }
