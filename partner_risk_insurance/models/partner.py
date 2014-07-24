# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009 Albert Cervera i Areny (http://www.nan-tic.com).
#    All Rights Reserved
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

from openerp.osv import orm, fields


class ResPartner(orm.Model):
    _inherit = 'res.partner'

    def _credit_limit(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for partner in self.browse(cr, uid, ids, context):
            res[partner.id] = (partner.company_credit_limit
                               + partner.insurance_credit_limit)
        return res

    _columns = {
        'credit_limit': fields.function(_credit_limit, method=True, store=True,
                                        string='Credit Limit', type='float'),
        'company_credit_limit': fields.float(
            "Company's Credit Limit", help='Credit limit granted by the '
            'company.'),
        'insurance_credit_limit': fields.float(
            "Insurance's Credit Limit", help='Credit limit granted by the '
            'insurance company.'),
        'risk_insurance_coverage_percent': fields.float(
            "Insurance's Credit Coverage", help='Percentage of the credit '
            'covered by the insurance.'),
        'risk_insurance_requested': fields.boolean(
            'Insurance Requested', help='Mark this field if an insurance was '
            'requested for the credit of this partner.'),
        'risk_insurance_grant_date': fields.date(
            'Insurance Grant Date', help='Date when the insurance was granted '
            'by the insurance company.'),
        'risk_insurance_code': fields.char(
            'Insurance Code', size=64, help='Code assigned to this partner by '
            'the risk insurance company.'),
        'risk_insurance_code_2': fields.char(
            'Insurance Code 2', size=64, help='Seconary code assigned to this '
            'partner by the risk insurance company.'),
    }
