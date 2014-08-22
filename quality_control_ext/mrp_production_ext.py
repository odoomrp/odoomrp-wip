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

class mrp_production(osv.osv):

    _inherit = 'mrp.production'
    
    def _count_created_test(self, cr, uid, ids, name, arg, context=None):
        if context == None:
            context = {}
        res = {}
        for test in self.browse(cr,uid,ids,context=context):
            num_created = 0
            if test.qc_test_ids:
                for line in test.qc_test_ids:
                    num_created = num_created + 1
                    
            res[test.id] = num_created

        return res
    
    
    def _count_realized_test(self, cr, uid, ids, name, arg, context=None):
        if context == None:
            context = {}
        res = {}
        for test in self.browse(cr,uid,ids,context=context):
            num_realized = 0
            if test.qc_test_ids:
                for line in test.qc_test_ids:
                    if line.state not in ('draft','waiting'):
                        num_realized = num_realized + 1
                    
            res[test.id] = num_realized

        return res
    
    def _count_ok_test(self, cr, uid, ids, name, arg, context=None):
        if context == None:
            context = {}
        res = {}
        for test in self.browse(cr,uid,ids,context=context):
            num_ok = 0
            if test.qc_test_ids:
                for line in test.qc_test_ids:
                    if line.success:
                        num_ok = num_ok + 1
                    
            res[test.id] = num_ok
                
        return res
    
    def _count_nook_test(self, cr, uid, ids, name, arg, context=None):
        if context == None:
            context = {}
        res = {}
        for test in self.browse(cr,uid,ids,context=context):
            num_nook = 0
            if test.qc_test_ids:
                for line in test.qc_test_ids:
                    if not line.success:
                        num_nook = num_nook + 1
                    
            res[test.id] = num_nook
                
        return res
    
    _columns = {# Tests asociados a la OF
                'qc_test_ids':fields.one2many('qc.test','production_id','Tests'),
                # Numero de test creados
                'created_tests': fields.function(_count_created_test, string="Created Tests", type="integer"),
                # Numero de test realizados
                'realized_tests': fields.function(_count_realized_test, string="Realized Tests", type="integer"),
                # Numero de test OK
                'ok_tests': fields.function(_count_ok_test, string="Tests OK", type="integer"),
                # Numero de test no OK
                'nook_tests': fields.function(_count_nook_test, string="Tests no OK", type="integer"),
                }
    
    def action_confirm(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        test_obj = self.pool.get('qc.test')
        result = super(mrp_production,self).action_confirm(cr,uid,ids,context=context)
        
        if ids:
            for production in self.browse(cr,uid,ids,context=context):
                if production.move_created_ids:
                    for move in production.move_created_ids:
                        how_many = move_obj._how_many_test_create(cr, uid, move.product_id,move.product_qty, context=context)
                        if how_many > 0:
                            move_obj._create_test_automatically(cr, uid, how_many, move, context=context)
                            production2 = self.browse(cr,uid,production.id)
                            if production2.qc_test_ids:
                                for test in  production2.qc_test_ids:
                                    test_obj.write(cr,uid,[test.id],{'stock_move_id': False},context=context)
        
        return result

mrp_production()
