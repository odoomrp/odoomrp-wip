# -*- encoding: utf-8 -*-
##############################################################################
#
#    Avanzosc - Advanced Open Source Consulting
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

from openerp.osv import orm
from openerp.tools.translate import _
import time


class StockMove(orm.Model):
    _inherit = 'stock.move'

    def _how_many_test_create(self, cr, uid, product, qty, context=None):
        rank_obj = self.pool['sample.rank']
        how_many = 0
        rank_ids = rank_obj.search(cr, uid, [('product_id', '=', product.id),
                                             ('category_id', '=', False)],
                                   limit=1, context=context)
        if not rank_ids:
            rank_ids = rank_obj.search(
                cr, uid, [('product_id', '=', False),
                          ('category_id', '=', product.categ_id.id)], limit=1,
                context=context)
        if not rank_ids:
            rank_ids = rank_obj.search(cr, uid, [('product_id', '=', False),
                                                 ('category_id', '=', False)],
                                       limit=1, context=context)
        if rank_ids:
            rank = rank_obj.browse(cr, uid, rank_ids[0], context=context)
            if rank.sample_rank_lines_ids:
                for line in rank.sample_rank_lines_ids:
                    if qty >= line.min and qty <= line.max:
                        how_many = line.how_many
        if how_many <= 0:
            raise orm.except_orm(
                _('Test Creation Error !'),
                _('Shows not found for product: %s, category: %s') %
                (product.name, product.categ_id.name))
        return how_many

    def _create_test_automatically(self, cr, uid, how_many, move,
                                   context=None):
        template_obj = self.pool['qc.test.template']
        test_obj = self.pool['qc.test']
        test_line_obj = self.pool['qc.test.line']
        template_ids = template_obj.search(
            cr, uid, [('product_id', '=', move.product_id.id),
                      ('active', '=', True)], context=context)
        if not template_ids:
            template_ids = template_obj.search(
                cr, uid,
                [('product_category_id', '=', move.product_id.categ_id.id),
                 ('product_id', '=', False),
                 ('active', '=', True)], context=context)
        if not template_ids:
            template_ids = template_obj.search(
                cr, uid, [('product_category_id', '=', False),
                          ('product_id', '=', False),
                          ('active', '=', True)], context=context)
        if not template_ids:
            raise orm.except_orm(
                _('Test Creation Error !'),
                _('No test template found for product: %s, category: %s') %
                (move.product_id.name, move.product_id.categ_id.name))
        else:
            for template in template_obj.browse(cr, uid, template_ids,
                                                context=context):
                # Creo la cabecera del test
                if move.picking_id:
                    origin = (str(move.picking_id.name) + ' - ' +
                              move.product_id.name)
                elif move.production_id:
                    origin = (str(move.production_id.name) + ' - ' +
                              move.product_id.name)
                data = {
                    'name': time.strftime('%Y%m%d %H%M%S'),
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
                test_id = test_obj.create(cr, uid, data, context=context)
                # Creo las líneas del test
                if template.test_template_line_ids:
                    count = 0
                    howmany = how_many
                    while howmany > 0:
                        count = count + 1
                        for line in template.test_template_line_ids:
                            data = {
                                'sequence': count,
                                'test_id': test_id,
                                'test_template_line_id': line.id,
                                'min_value': line.min_value,
                                'max_value': line.max_value
                            }
                            if line.uom_id:
                                data.update({'uom_id': line.uom_id.id})
                            if line.proof_id:
                                data.update({'proof_id': line.proof_id.id})
                            if line.method_id:
                                data.update({'method_id': line.method_id.id})
                            if line.type:
                                data.update({'proof_type': line.type})
                                if (line.type == 'qualitative' and
                                        line.valid_value_ids):
                                    data.update({'actual_value_ql': (
                                                len(line.valid_value_ids)
                                                and line.valid_value_ids[0]
                                                and line.valid_value_ids[0].id
                                                or False)})
                                    my_data = []
                                    for val in line.valid_value_ids:
                                        my_data.append(val.id)
                                    if my_data:
                                        data.update({'valid_value_ids':
                                                     [(6, 0, my_data)]})
                            test_line_obj.create(cr, uid, data,
                                                 context=context)
                        howmany -= 1
        return True
