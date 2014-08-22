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
import time
import decimal_precision as dp

class qc_test(osv.osv):

    _inherit = 'qc.test'
    
    def _get_categ(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for test in self.browse(cr, uid, ids):
            if test.product_id:
                if test.product_id.categ_id:
                    res[test.id] = test.product_id.categ_id.id
                else:
                    res[test.id] = False
            else:
                res[test.id] = False

        return res
    
    _columns = {'name': fields.char('Date',size=20, required=True, readonly=True, states={'draft':[('readonly',False)]}, select="1"),
                'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product UoM')),
                # Origen
                'origin': fields.char('Origin', size=128),
                # Test asociados al movimiento
                'stock_move_id':fields.many2one('stock.move', 'Move', ondelete='cascade'),
                # Producto del movimiento
                'product_id':fields.many2one('product.product', 'Product'),
                # Categoria del producto
                'categ_id': fields.function(_get_categ, type='many2one', relation='product.category', string='Category', store=True),
                # Albarán del movimiento
                'picking_id':fields.many2one('stock.picking', 'Picking'),
                # Orden de producción del movimiento
                'production_id':fields.many2one('mrp.production', 'Production'),
                }
    
    _defaults = {'name' : lambda *a: str(time.strftime('%Y%m%d%H%M%S')),
                 }
    
    def write(self, cr, uid, ids, vals, context=None):
        if context == None:
            context={}
        move_obj = self.pool.get('stock.move')
                
        result = super(qc_test, self).write(cr, uid, ids, vals, context=context)
        
        if ids:
            if not isinstance(ids,list):
                ids=[ids]
            for test in self.browse(cr,uid,ids):
                if test.stock_move_id:
                    move_obj.write(cr,uid,[test.stock_move_id.id],{},context=context)              

        return result
    
    def onchange_product(self, cr, uid, ids, product_id, context=None):
        if context == None:
            context = {}
        res = {'categ_id': False,} 
        product_obj = self.pool.get('product.product')
        
        if product_id:
            product = product_obj.browse(cr,uid,product_id,context=context)
            if product.categ_id:
                res.update({'categ_id': product.categ_id.id})

        return {'value': res}  
    
    def button_create_test_lines(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
            
        move_obj = self.pool.get('stock.move')
        template_obj = self.pool.get('qc.test.template')
        test_line_obj = self.pool.get('qc.test.line')
            
        if ids:
            for test in self.browse(cr,uid,ids,context=context):
                if test.test_template_id:
                    how_many = move_obj._how_many_test_create(cr, uid, test.product_id,test.product_qty, context=context)
                    if how_many > 0:
                        max_sequence = 0
                        if test.test_line_ids:
                            for line in test.test_line_ids:
                                if line.sequence > max_sequence:
                                    max_sequence = line.sequence
                                    
                        template = template_obj.browse(cr,uid,test.test_template_id.id,context=context)
                                    
                        # Creo las líneas del test
                        if template.test_template_line_ids:
                            count = 0
                            howmany = how_many
                            while howmany > 0: 
                                count = count + 1
                                for line in template.test_template_line_ids:
                                    sequence = max_sequence + count
                                    data = {'sequence': sequence,
                                            'test_id': test.id,
                                            'test_template_line_id': line.id,      
                                            'min_value': line.min_value,
                                            'max_value': line.max_value      
                                           }
                                    if line.uom_id:
                                        data.update({'uom_id': line.uom_id.id,})
                                    if line.proof_id:
                                        data.update({'proof_id': line.proof_id.id,})
                                    if line.method_id:
                                        data.update({'method_id': line.method_id.id,})                    
                                    if line.type:
                                        data.update({'proof_type': line.type,})   
                                        
                                    test_line_id = test_line_obj.create(cr,uid,data,context=context)  
                                    
                                howmany = howmany - 1



        return True

qc_test()
