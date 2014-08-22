# -*- encoding: utf-8 -*-
##############################################################################
#
#    Avanzosc - Avanced Open Source Consulting
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
from osv import osv
from osv import fields
from tools.translate import _

class qc_test(osv.osv):

    _inherit = 'qc.test'
    
    _columns = {'valid':fields.boolean('Valid', select="1"),
                }
    
    def write(self, cr, uid, ids, vals, context=None):
        found = False
        if vals.has_key('state'):
            state = vals.get('state')
            if state == 'success':
                found = True
                
        if found:
            vals.update({'valid': True})
                
        result = super(qc_test, self).write(cr, uid, ids, vals, context=context)

        return result

qc_test()
