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

class stock_move(osv.osv):

    _inherit = 'stock.move'

    
    def _how_many_test_create(self, cr, uid, product, qty, context=None):
        if context == None:
            context = {}
            
        rank_obj = self.pool.get('sample.rank')
        
        how_many = 0
        rank_ids = rank_obj.search(cr, uid, [('product_id','=', product.id), 
                                             ('category_id','=', False),], limit=1, context=context)
        
        if not rank_ids:
            rank_ids = rank_obj.search(cr, uid, [('product_id','=', False), 
                                                 ('category_id','=', product.categ_id.id),], limit=1, context=context)

        if not rank_ids:
            rank_ids = rank_obj.search(cr, uid, [('product_id','=', False), 
                                                 ('category_id','=', False),], limit=1, context=context)
            
        rank_id = 0
        product_rank_id = 0
        categ_rank_id = 0
        general_rank_id = 0
        if rank_ids:
            for rank in rank_obj.browse(cr, uid, rank_ids, context=context):
                if rank.product_id:
                    product_rank_id = rank.id
                else:
                    if rank.category_id:
                        categ_rank_id = rank.id
                    else:
                        general_rank_id = rank.id
                        
            if general_rank_id > 0:
                rank_id = general_rank_id
            if categ_rank_id > 0:
                rank_id = categ_rank_id
            if product_rank_id > 0:
                rank_id = product_rank_id
                
            rank = rank_obj.browse(cr,uid, rank_id, context=context)
            if rank.sample_rank_lines_ids:
                for line in rank.sample_rank_lines_ids:
                    if qty >= line.fromm and qty <= line.to:
                        how_many = line.how_many
                        
        if how_many == 0 or how_many < 0:
            raise osv.except_osv(_('Test Creation Error !'), _('Shows not found for product: %s, category:%s') % (product.name,product.categ_id.name,))
            
        return how_many
    
    def _create_test_automatically(self, cr, uid, how_many, move, context=None):

        if context == None:
            context = {}
            
        template_obj = self.pool.get('qc.test.template')
        test_obj = self.pool.get('qc.test')
        test_line_obj = self.pool.get('qc.test.line')
        attachment_obj = self.pool.get('ir.attachment')
        
        template_ids = template_obj.search(cr, uid, [('product_id','=', move.product_id.id), 
                                                     ('active','=', True),], context=context)
        if not template_ids:
            template_ids = template_obj.search(cr, uid, [('product_category_id','=', move.product_id.categ_id.id), 
                                                         ('product_id','=',False),
                                                         ('active','=', True),], context=context)
            if not template_ids:
                template_ids = template_obj.search(cr, uid, [('product_category_id','=', False), 
                                                             ('product_id','=',False),
                                                             ('active','=', True),], context=context)
                if not template_ids:
                    raise osv.except_osv(_('Test Creation Error !'), _('No test template found for product: %s, category:%s') % (move.product_id.name,move.product_id.categ_id.name,))

        if template_ids:
            for template in template_obj.browse(cr,uid,template_ids,context=context):
                # Creo la cabecera del test
                if move.picking_id:
                    origin = str(move.picking_id.name) + ' - ' + move.product_id.name
                else:
                    if move.production_id:
                        origin = str(move.production_id.name) + ' - ' + move.product_id.name
                # Cojo los archivos adjuntos compartidos
                new_attachment = []
                if template.attachment_ids:
                    for attachment in template.attachment_ids:
                        new_attachment.append(attachment.id)     
                # Cojo los archivos adjuntos NO compartidos
                attachment_ids = attachment_obj.search(cr, uid, [('res_model','=', 'qc.test.template'), 
                                                                 ('res_id','=',template.id),], context=context)
                                  
                data = {'name': time.strftime('%Y%m%d %H%M%S'),
                        'test_template_id': template.id,
                        'origin': origin,               
                        'enabled': True,                   
                        'product_id': move.product_id.id,
                        'state': 'draft',
                        'product_qty': move.product_qty,
                        'stock_move_id': move.id,
                       }
                if move.picking_id:
                    data.update({'picking_id': move.picking_id.id})
                if move.production_id:
                    data.update({'production_id': move.production_id.id})
                if new_attachment:
                    data.update({'attachment_ids':  [(6,0,new_attachment)],}) 
                test_id = test_obj.create(cr,uid,data,context=context)
                if attachment_ids:
                    for attachment_id in attachment_ids:
                        new_attachment_id = attachment_obj.copy(cr, uid, attachment_id)  
                        attachment_obj.write(cr,uid,[new_attachment_id],{'res_model': 'qc.test',
                                                                         'res_id': test_id})     
                # Creo las líneas del test
                if template.test_template_line_ids:
                    count = 0
                    howmany = how_many
                    while howmany > 0: 
                        count = count + 1
                        for line in template.test_template_line_ids:
                            data = {'sequence': count,
                                    'test_id': test_id,
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
                                if line.type == 'qualitative' and line.valid_value_ids:        
                                    data.update({'actual_value_ql': len(line.valid_value_ids) and line.valid_value_ids[0] and  line.valid_value_ids[0].id or False,})
                                    my_data = []
                                    for val in line.valid_value_ids:
                                        my_data.append(val.id)
                                    if my_data:
                                        data.update({'valid_value_ids': [(6,0,my_data)],}) 
                                
                            test_line_id = test_line_obj.create(cr,uid,data,context=context)  
                            
                        howmany = howmany - 1

        return True

stock_move()
