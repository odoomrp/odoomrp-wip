# -*- encoding: utf-8 -*-
##############################################################################
#
#    Avanzosc - Avanced Open Source Consulting
#    Copyright (C) 2011 - 2013 Avanzosc <http://www.avanzosc.com>
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
class qc_test_line(osv.osv):

    _inherit = 'qc.test.line'
    _order = 'sequence'
    
    _columns = {'sequence': fields.integer('Sequence', readonly=True),
                }
    
    def create(self, cr, uid, data, context=None):
        if not data.has_key('sequence'):
            data.update({'sequence': 1})
            
        picking_obj = self.pool.get('stock.picking')
        production_obj = self.pool.get('mrp.production')
            
        new_id = super(qc_test_line,self).create(cr,uid,data,context=context)
        
        line = self.browse(cr,uid,new_id)
        
        if line.test_id:
            if line.test_id.picking_id:
                picking_obj.write(cr,uid,[line.test_id.picking_id.id],{},context=context) 
            if line.test_id.production_id:
                production_obj.write(cr,uid,[line.test_id.production_id.id],{},context=context)
                
        
        return new_id
    
    def write(self, cr, uid, ids, vals, context=None):
        if context == None:
            context = {}
            
        picking_obj = self.pool.get('stock.picking')
        production_obj = self.pool.get('mrp.production')
        
        result = super(qc_test_line,self).write(cr, uid, ids, vals, context)
        
        if ids:
            for line in self.browse(cr,uid,ids,context=context):
                if line.test_id:
                    if line.test_id.picking_id:
                        picking_obj.write(cr,uid,[line.test_id.picking_id.id],{},context=context) 
                    if line.test_id.production_id:
                        production_obj.write(cr,uid,[line.test_id.production_id.id],{},context=context)
                    
        return result

qc_test_line()
