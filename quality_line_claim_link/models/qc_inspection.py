# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _


class QcInspection(models.Model):
    _inherit = 'qc.inspection'

    @api.multi
    def action_approve(self):
        category_obj = self.env['crm.case.categ']
        nc_category_search = [('name', '=', 'NC')]
        idi_category_search = [('name', '=', 'IDI')]
        super(QcInspection, self).action_approve()
        idi_categ = False
        nc_categ = False
        for inspection in self:
            for line in inspection.inspection_lines:
                if line.tolerance_status == 'not_tolerable':
                    if not nc_categ:
                        nc_categ = category_obj.search(nc_category_search,
                                                       limit=1)
                        if not nc_categ:
                            raise exceptions.Warning(
                                _("NC crm case category NOT FOUND"))
                    inspection.make_claim_from_inspection_line(line, nc_categ)
                elif line.tolerance_status == 'not_tolerable':
                    if not idi_categ:
                        idi_categ = category_obj.search(idi_category_search,
                                                        limit=1)
                        if not idi_categ:
                            raise exceptions.Warning(
                                _("IDI crm case category NOT FOUND"))
                    inspection.make_claim_from_inspection_line(line, idi_categ)

    def make_claim_from_inspection_line(self, line, categ):
        crm_claim_obj = self.env['crm.claim']
        crm_claim_obj.create({
            'name': _('Quality test %s for product %s unsurpassed, in test'
                      ' line %s')
            % (self.name, self.object_id.name, line.name),
            'date': fields.Datetime.now(),
            'ref': '%s,%s' % (self.object_id._model, self.object_id.id),
            'inspection_id': self.id,
            'categ_id': categ.id})
