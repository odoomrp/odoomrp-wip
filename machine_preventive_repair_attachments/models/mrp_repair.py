# -*- coding: utf-8 -*-
# (c) 2016 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class MrpRepair(models.Model):
    _inherit = 'mrp.repair'

    @api.multi
    def show_attachments(self):
        document_obj = self.env['ir.attachment']
        attachmen_lst = []
        for machine_op in self.preventive_operations:
            attachments = document_obj.search(
                [('res_model', '=', 'preventive.operation.type'),
                 ('res_id', '=', machine_op.opname_omm.optype_id.id)])
            attachmen_lst.append(attachments.ids)
        search_view = self.env.ref('base.view_attachment_search')
        idform = self.env.ref('base.view_attachment_form')
        idtree = self.env.ref('base.view_attachment_tree')
        kanban = self.env.ref('mail.view_document_file_kanban')
        return {
            'view_type': 'form',
            'view_mode': 'kanban, tree, form',
            'res_model': 'ir.attachment',
            'views': [(kanban.id, 'kanban'), (idtree.id, 'tree'),
                      (idform.id, 'form')],
            'search_view_id': search_view.id,
            'view_id': kanban.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': "[('id','in',[" +
            ','.join(map(str, attachmen_lst)) + "])]",
            'context': self.env.context,
            }
