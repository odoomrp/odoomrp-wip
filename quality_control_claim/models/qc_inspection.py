# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _


class QcInspection(models.Model):
    _inherit = 'qc.inspection'

    @api.one
    def _count_claims(self):
        claim_obj = self.env['crm.claim']
        cond = [('ref', '=', '%s,%s' % (self._model, self.id))]
        claims = claim_obj.search(cond)
        self.claims = len(claims)

    automatic_claims = fields.Boolean(
        'Automatic Claims', default=False,
        help="If you want to create one claim when the quality test status is"
             " 'Quality failed'.")
    automatic_claims_by_line = fields.Boolean(
        'Automatic Claims by line', default=False,
        help="If you want to create one claim per quality test line, when the"
             " quality test line status is 'Tolerable' or 'Not Tolerable'.")
    claims = fields.Integer(string="Created claims",
                            compute='_count_claims', store=False)

    @api.multi
    def _prepare_inspection_header(self, object_ref, test):
        result = super(QcInspection, self)._prepare_inspection_header(
            object_ref, test)
        result.update({'automatic_claims': test.automatic_claims,
                       'automatic_claims_by_line':
                       test.automatic_claims_by_line})
        return result

    @api.multi
    def action_approve(self):
        crm_claim_obj = self.env['crm.claim']
        category_obj = self.env['crm.case.categ']
        nc_category_search = [('name', '=', 'NC')]
        idi_category_search = [('name', '=', 'IDI')]
        nc_categ = category_obj.search(nc_category_search, limit=1)
        if not nc_categ:
            raise exceptions.Warning(
                _("NC crm case category NOT FOUND"))
        idi_categ = category_obj.search(idi_category_search, limit=1)
        if not idi_categ:
            raise exceptions.Warning(
                _("IDI crm case category NOT FOUND"))
        super(QcInspection, self).action_approve()
        for inspection in self:
            if inspection.state == 'failed' and inspection.automatic_claims:
                vals = inspection.init_claim_vals()
                vals['name'] = _('Quality test %s for product %s'
                                 ' unsurpassed') % (self.name,
                                                    self.object_id.name)
                crm_claim_obj.create(vals)
            if inspection.automatic_claims_by_line:
                for line in inspection.inspection_lines:
                    if line.tolerance_status == 'not_tolerable':
                        vals = inspection.init_claim_vals_line(line)
                        vals['categ_id'] = nc_categ.id
                        crm_claim_obj.create(vals)
                    elif line.tolerance_status == 'tolerable':
                        vals = inspection.init_claim_vals_line(line)
                        vals['categ_id'] = idi_categ.id
                        crm_claim_obj.create(vals)

    def init_claim_vals(self):
        vals = {'date': fields.Datetime.now(),
                'ref': '%s,%s' % (self._model, self.id)
                }
        return vals

    def init_claim_vals_line(self, line):
        vals = self.init_claim_vals()
        vals['name'] = _('Quality test %s for product %s unsurpassed, in test'
                         ' line %s') % (self.name,
                                        self.object_id.name, line.name)
        return vals
