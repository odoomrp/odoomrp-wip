# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class CrmClaim(models.Model):
    _inherit = 'crm.claim'

    corrective_id = fields.Many2one(
        comodel_name='crm.claim.corrective', string='Corrective Action Info',
        oldname='aaccseq')
    description_id = fields.Many2one(
        comodel_name='crm.claim.problem.description',
        string='Problem Description', help='Select a problem description.')
    decision_id = fields.Many2one(
        comodel_name='crm.claim.decision', string='Decision',
        help='Select a decision.')
    decision_desc = fields.Text(string='Description', oldname='desc_decis')
    cause_id = fields.Many2one(
        comodel_name='crm.claim.problem.cause', string='Cause',
        help='Select a cause.')
    cause_desc = fields.Text(string='Cause Description', oldname='desc_cause')
    moddate = fields.Date(string='Date')
    ncdecision_id = fields.Many2one(
        comodel_name='crm.claim.decision', string='Nonconformity Decision',
        help='Select a decision for nonconformity. If you change this the '
        'description of nonconformity will be updated.',
        oldname='nfdecision_id')
    ncdecision_desc = fields.Text(
        string='Nonconformity Decision Description', oldname='nfdesc_decis')

    @api.model
    def create(self, values):
        result = super(CrmClaim, self).create(values)
        if result.corrective_id:
            result.corrective_id.write({'claim_id': result.id})
        return result

    @api.multi
    def write(self, values):
        result = super(CrmClaim, self).write(values)
        if 'corrective_id' in values:
            for record in self:
                record.corrective_id.write({'claim_id': record.id})
        return result

    @api.onchange('decision_id')
    def onchange_decision_id(self):
        if self.decision_id:
            decision_texts = []
            if self.decision_desc:
                decision_texts.append(self.decision_desc)
            decision_texts.append(
                self.decision_id.description or self.decision_id.name)
            self.desc_decis = '\n'.join(decision_texts)

    @api.onchange('ncdecision_id')
    def onchange_ncdecision_id(self):
        if self.ncdecision_id:
            ncdecision_texts = []
            if self.ncdecision_desc:
                ncdecision_texts.append(self.ncdecision_desc)
            ncdecision_texts.append(
                self.ncdecision_id.description or self.ncdecision_id.name)
            self.ncdecision_desc = '\n'.join(ncdecision_texts)

    @api.onchange('description_id')
    def onchange_description_id(self):
        if self.description_id:
            description_texts = []
            if self.description:
                description_texts.append(self.description)
            description_texts.append(
                self.description_id.description or self.description_id.name)
            self.description = '\n'.join(description_texts)

    @api.onchange('corrective_id')
    def onchange_corrective_id(self):
        if self.corrective_id:
            description_texts = []
            if self.decision_desc:
                description_texts.append(self.decision_desc)
            description_texts.append(
                self.corrective_id.description or self.corrective_id.name)
            for solution in self.corrective_id.sol_ids:
                description_texts.append(
                    '%s %s' % (solution.sequence,
                               (solution.description or solution.name)))
            self.decision_desc = '\n'.join(description_texts)

    @api.onchange('cause_id')
    def onchange_cause_id(self):
        if self.cause_id:
            cause_texts = []
            if self.cause:
                cause_texts.append(self.cause)
            cause_texts.append(self.cause_id.description or self.cause_id.name)
            self.cause = '\n'.join(cause_texts)


class CrmClaimCorrective(models.Model):
    _name = 'crm.claim.corrective'
    _inherit = ['mail.thread']
    _rec_name = 'code'

    @api.model
    def default_get(self, fields):
        res = super(CrmClaimCorrective, self).default_get(fields)
        if self.env.context.get('cause_id_value'):
            action_lst = []
            cause = self.env['crm.claim.problem.cause'].browse(
                self.env.context.get('cause_id_value'))
            sequence = 0
            for solution in cause.solution_ids:
                action_values = {
                    'sequence': sequence,
                    'name': solution.name,
                    'description': solution.description,
                }
                action_lst.append(action_values)
                sequence += 1
            res.update(sol_ids=action_lst)
        return res

    @api.multi
    def name_get(self):
        res = super(CrmClaimCorrective, self).name_get()
        res = []
        for record in self:
            res.append(
                (record.id, "[%s] %s" % (record.code, record.name)))
        return res

    code = fields.Char(
        string='Code', default='/', oldname='seq', readonly=True)
    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    claim_id = fields.Many2one(
        comodel_name='crm.claim', string='Claim',
        help='Select a Claim', readonly=True, copy=False)
    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Partner',
        related='claim_id.partner_id', store=True, readonly=True)
    sol_ids = fields.One2many(
        comodel_name='crm.claim.corrective.action',
        inverse_name='corrective_id', string='Corrective Actions')
    state = fields.Selection(
        selection=[('new', 'New'), ('pending', 'Pending'),
                   ('closed', 'Closed')], string='State', readonly=True,
        default='new', track_visibility='always')

    @api.model
    def create(self, vals):
        if vals.get('code', '/') == '/':
            vals['code'] = self.env['ir.sequence'].get('crm.claim.corrective')
        return super(CrmClaimCorrective, self).create(vals)

    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        default['code'] = self.env['ir.sequence'].get('crm.claim.corrective')
        return super(CrmClaimCorrective, self).copy(default)


class CrmClaimDecision(models.Model):
    _name = 'crm.claim.decision'

    name = fields.Char(string='Decision Name', required=True)
    description = fields.Text(string='Description')


class CrmClaimProblemDescription(models.Model):
    _name = 'crm.claim.problem.description'

    name = fields.Char(string='Description Name', required=True)
    description = fields.Text(string='Description')


class CrmClaimProblemCause(models.Model):
    _name = 'crm.claim.problem.cause'

    name = fields.Char(string='Cause Name', required=True)
    description = fields.Text(string='Description')
    solution_ids = fields.Many2many(
        comodel_name='crm.claim.problem.solution',
        relation='rel_cause_solution', column1='solution_id',
        column2='cause_id', string='Solutions')


class CrmClaimProblemSolution(models.Model):
    _name = 'crm.claim.problem.solution'

    name = fields.Char(string='Solution Name', required=True)
    description = fields.Text(string='Description')
    cause_ids = fields.Many2many(
        comodel_name='crm.claim.problem.cause', relation='rel_cause_solution',
        column1='cause_id', column2='solution_id', string='Causes')


class CrmClaimCorrectiveAction(models.Model):
    _name = 'crm.claim.corrective.action'

    name = fields.Char(string='Name', required=True)
    sequence = fields.Integer(string='Sequence')
    description = fields.Text(string='Description')
    responsible_id = fields.Many2one(
        comodel_name='res.users', string='Responsible',
        help='Select a responsible')
    date_planned = fields.Date(string='Planned Date')
    date_done = fields.Date(string='Date Done')
    corrective_id = fields.Many2one(
        comodel_name='crm.claim.corrective', string='Corrective action')
    claim_id = fields.Many2one(
        comodel_name='crm.claim', string='Claim',
        related='corrective_id.claim_id', store=True)
