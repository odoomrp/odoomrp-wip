# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from lxml import etree

from openerp.osv.orm import BaseModel


class BaseModelInherit(BaseModel):
    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        """
        Get the detailed composition of the requested view like fields, model,
        view architecture

        :param view_id: id of the view or None
        :param view_type: type of the view to return if view_id is None
            ('form', tree', ...)
        :param toolbar: true to include contextual actions
        :param submenu: deprecated
        :return: dictionary describing the composition of the requested view
            (including inherited views and extensions)
        :raise AttributeError:
                            * if the inherited view has unknown position to
                                work with other than 'before', 'after',
                                'inside', 'replace'
                            * if some tag other than 'position' is found in
                                parent view
        :raise Invalid ArchitectureError: if there is view type other than
            form, tree, calendar, search etc defined on the structure
        """
        if context is None:
            context = {}

        result = super(BaseModelInherit,
                       self).fields_view_get(cr, uid, view_id=view_id,
                                             view_type=view_type,
                                             context=context,
                                             toolbar=toolbar,
                                             submenu=submenu)
        if view_type == 'form':
            model_obj = self.pool['ir.model']
            step_obj = self.pool['step.config']

            model_id = model_obj.search(cr, uid,
                                        [('name', '=', result['model'])],
                                        context=context)[0]
            step_ids = step_obj.search(cr, uid, [('model_id', '=', model_id)],
                                       context=context)

            for step_id in step_ids:
                doc = etree.XML(result['arch'])
                step = step_obj.browse(cr, uid, step_id, context=context)

                nodes = doc.xpath('//header')
                if not nodes:
                    node = etree.Element('header')
                else:
                    node = nodes[0]

                for line in step.line_ids:
                    line_node = etree.SubElement(node, 'button')
                    line_node.set('name', line.button)

                result['arch'] = etree.tostring(doc)

        return result
