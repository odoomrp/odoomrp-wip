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

class qc_test_set_template_wizard(osv.osv_memory):

    _inherit = 'qc.test.set.template.wizard'
    
    def _default_product_id(self, cr, uid, context):
        id = context.get('active_id',False)
        if not id:
            return False
        test = self.pool.get('qc.test').browse(cr, uid, id, context)
        if test.product_id:
            return test.product_id.id
        else:
            return False
        
    def _default_product_category_id(self, cr, uid, context):
        id = context.get('active_id',False)
        if not id:
            return False
        test = self.pool.get('qc.test').browse(cr, uid, id, context)
        if test.product_id:
            if test.product_id.categ_id:
                return test.product_id.categ_id.id
            else:
                return False
        else:
            return False
    
    _columns = {# Producto
                'product_id':fields.many2one('product.product', 'Product'),
                # Categoria
                'product_category_id':fields.many2one('product.category', 'Product Category'),
                }
    
    _defaults = {'product_id': _default_product_id,
                 'product_category_id': _default_product_category_id,
                 }

    def action_create_test(self, cr, uid, ids, context):
        template_obj = self.pool.get('qc.test.template')
        test_obj = self.pool.get('qc.test')
        attachment_obj = self.pool.get('ir.attachment')
        wizard = self.browse(cr, uid, ids[0], context)
        template = template_obj.browse(cr,uid,wizard.test_template_id.id, context=context)
        
        # Cojo los archivos adjuntos compartidos
        new_attachment = []
        if template.attachment_ids:
            for attachment in template.attachment_ids:
                new_attachment.append(attachment.id)   
        if new_attachment:
            test_obj.write(cr,uid,[context['active_id']],{'attachment_ids':  [(6,0,new_attachment)],},context=context)
            
        # Cojo los archivos adjuntos NO compartidos
        attachment_ids = attachment_obj.search(cr, uid, [('res_model','=', 'qc.test.template'), 
                                                         ('res_id','=', template.id)], context=context)
        if attachment_ids:
            for attachment_id in attachment_ids:
                new_attachment_id = attachment_obj.copy(cr, uid, attachment_id)  
                attachment_obj.write(cr,uid,[new_attachment_id],{'res_model': 'qc.test',
                                                                 'res_id': context['active_id']})    
        
        return super(qc_test_set_template_wizard,self).action_create_test(cr, uid, ids, context=context)

qc_test_set_template_wizard()
