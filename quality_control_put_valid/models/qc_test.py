# -*- encoding: utf-8 -*-
##############################################################################
#
#    Avanzosc - Advanced Open Source Consulting
#    Copyright (C) 2011 - 2014 Avanzosc <http://www.avanzosc.com>
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
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp.osv import orm, fields


class QcTest(orm.Model):
    _inherit = 'qc.test'

    _columns = {
        'valid': fields.boolean('Valid', select="1"),
    }

    def write(self, cr, uid, ids, vals, context=None):
        if 'state' in vals:
            if vals['state'] == 'success':
                vals.update({'valid': True})
        result = super(QcTest, self).write(cr, uid, ids, vals, context=context)
        return result
