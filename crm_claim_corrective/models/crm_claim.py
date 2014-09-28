# -*- encoding: utf-8 -*-
##############################################################################
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

from openerp.osv import orm, fields


class CrmClaim(orm.Model):
    _inherit = 'crm.claim'

    _columns = {
        # 'photo1': fields.binary('Photo1', filters='*.png,*.jpg'),
        # 'photo2': fields.binary('Photo2', filters='*.png,*.jpg'),
        # 'photo3': fields.binary('Photo3', filters='*.png,*.jpg'),
        # 'photo4': fields.binary('Photo4', filters='*.png,*.jpg'),
        'aaccseq': fields.many2one('crm.claim.corrective',
                                   'Corrective Action Info', size=64,
                                   required=False),
        'description_id': fields.many2one('crm.claim.problem.description',
                                          'Problem description',
                                          help='Select a Problem Description'),
        'decision_id': fields.many2one('crm.claim.decision', 'Decision',
                                       help='Select a Decision'),
        'cause_id': fields.many2one('crm.claim.problem.cause', 'Cause',
                                    help='Select a Cause'),
        'desc_decis': fields.text('Description', size=256),
        'desc_cause': fields.text('Cause Description', size=256),
        'moddate': fields.date('Fecha'),
        'nfdecision_id': fields.many2one('crm.claim.decision', 'Decision',
                                         help='Select a Decision'),
        'nfdesc_decis': fields.text('Description', size=256),
    }

    def create(self, cr, uid, data, context=None):
        corrective_obj = self.pool['crm.claim.corrective']
        new_id = super(CrmClaim, self).create(cr, uid, data, context=context)
        claim = self.browse(cr, uid, new_id)
        if claim.aaccseq:
            corrective_obj.write(cr, uid, [claim.aaccseq.id],
                                 {'claim_id': new_id}, context=context)
        return new_id

    def write(self, cr, uid, ids, vals, context=None):
        corrective_obj = self.pool['crm.claim.corrective']
        found = False
        if 'aaccseq' in vals:
            my_aaccseq = vals.get('aaccseq')
            found = True
            claim = self.browse(cr, uid, ids[0], context=context)
            if claim.aaccseq:
                corrective_obj.write(cr, uid, [claim.aaccseq.id],
                                     {'claim_id': False}, context=context)

        result = super(CrmClaim, self).write(cr, uid, ids, vals,
                                             context=context)

        if ids and found:
            if my_aaccseq:
                corrective_obj.write(cr, uid, [my_aaccseq],
                                     {'claim_id': ids[0]},
                                     context=context)

        return result

    def onchange_decision(self, cr, uid, ids, decision_id, context=None):
        if decision_id:
            decision_inicial = ''
            if ids:
                if isinstance(ids, list):
                    ids = ids[0]
                decision = self.read(cr, uid, ids, ['desc_decis'],
                                     context=context)
                if decision and decision['desc_decis']:
                    decision_inicial = decision['desc_decis']
                if decision_inicial != '':
                    decision_inicial += '\n'
            decision_obj = self.pool['crm.claim.decision']
            descript = decision_obj.browse(cr, uid, decision_id,
                                           context=context)
            decision_text = decision_inicial + descript.name
            res = {'desc_decis': decision_text}
            return {'value': res}

    def onchange_nfdecision(self, cr, uid, ids, nfdecision_id, context=None):
        if nfdecision_id:
            nfdecision_inicial = ''
            if ids:
                if isinstance(ids, list):
                    ids = ids[0]
                decision = self.read(cr, uid, ids, ['nfdesc_decis'],
                                     context=context)
                if decision and decision['nfdesc_decis']:
                    nfdecision_inicial = decision['nfdesc_decis']
                if nfdecision_inicial != '':
                    nfdecision_inicial += '\n'
            decision_obj = self.pool['crm.claim.decision']
            decision = decision_obj.browse(cr, uid, nfdecision_id,
                                           context=context)
            decision_text = nfdecision_inicial + decision.name
            res = {'nfdesc_decis': decision_text}
            return {'value': res}

    def onchange_description(self, cr, uid, ids, description_id, context=None):
        if description_id:
            description_inicial = ''
            if ids:
                if isinstance(ids, list):
                    ids = ids[0]
                description = self.read(cr, uid, ids, ['description'],
                                        context=context)
                if description and description['description']:
                    description_inicial = description['description']
                if description_inicial != '':
                    description_inicial += '\n'
            description_obj = self.pool['crm.claim.problem.description']
            description = description_obj.browse(cr, uid, description_id,
                                                 context=context)
            description_text = description_inicial + description.name
            res = {'description': description_text}
            return {'value': res}

    def onchange_cause(self, cr, uid, ids, cause_id, context=None):
        if cause_id:
            initial_cause = ''
            if ids:
                if isinstance(ids, list):
                    ids = ids[0]
                cause = self.read(cr, uid, ids, ['cause'], context=context)
                if cause and cause['cause']:
                    initial_cause = cause['cause']
                if initial_cause != '':
                    initial_cause += '\n'
            cause_obj = self.pool['crm.claim.problem.cause']
            cause = cause_obj.browse(cr, uid, cause_id, context=context)
            cause_text = initial_cause + cause.name
            res = {'cause': cause_text}
            return {'value': res}


class CrmClaimCorrective(orm.Model):
    _name = 'crm.claim.corrective'
    _rec_name = 'seq'

    def default_get(self, cr, uid, fields_list, context=None):
        res = super(CrmClaimCorrective, self).default_get(cr, uid,
                                                          fields_list,
                                                          context=context)
        if not context:
            context = {}
        cause_obj = self.pool['crm.claim.problem.cause']
        correct_actions_lst = []
        if 'cause_id_value' in context and context['cause_id_value']:
            cause = cause_obj.browse(cr, uid, context['cause_id_value'],
                                     context=context)
            kont = 0
            for solution in cause.solution_ids:
                correct_actions_vals = {
                    'name': solution.name,
                    'sequence': kont,
                }
                correct_actions_lst.append(correct_actions_vals)
                kont += 1
        res.update({'sol_ids': correct_actions_lst})
        return res

    _columns = {
        'seq': fields.char('Sequence', size=64, required=True),
        'claim_id': fields.many2one('crm.claim', 'Claim',
                                    help='Select a Claim', readonly=True),
        'partner_id': fields.related('claim_id', 'partner_id', type="many2one",
                                     relation='res.partner', string='Customer',
                                     store=True, readonly=True),
        'sol_ids': fields.one2many('crm.claim.corrective.action',
                                   'corrective_action_id',
                                   'Corrective Action'),
        'state': fields.selection([('new', 'New'),
                                   ('pending', 'Pending'),
                                   ('closed', 'Closed'),
                                   ], 'State', readonly=True),
    }

    _defaults = {
        'state': 'new',
        'seq': lambda obj, cr, uid, context: obj.pool['ir.sequence'].get(
            cr, uid, 'crm.claim.corrective', context=context),
    }

    def action_new(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'new'}, context=context)
        return True

    def action_pending(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'pending'}, context=context)
        return True

    def action_close(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'closed'}, context=context)
        return True


class CrmClaimDecision(orm.Model):
    _name = 'crm.claim.decision'

    _columns = {
        'name': fields.text('Decision', size=256, required=True),
    }


class CrmClaimProblemDescription(orm.Model):
    _name = 'crm.claim.problem.description'

    _columns = {
        'name': fields.text('Description', size=256, required=True),
    }


class CrmClaimProblemCause(orm.Model):
    _name = 'crm.claim.problem.cause'

    _columns = {
        'name': fields.text('Cause', size=256, required=True),
        'solution_ids': fields.many2many('crm.claim.problem.solution',
                                         'rel_cause_solution', 'solution_id',
                                         'cause_id', 'Solutions'),
    }


class CrmClaimProblemSolution(orm.Model):
    _name = 'crm.claim.problem.solution'

    _columns = {
        'name': fields.text('Solution', size=256, required=True),
        'cause_ids': fields.many2many('crm.claim.problem.cause',
                                      'rel_cause_solution', 'cause_id',
                                      'solution_id', 'Causes'),
    }


class CrmClaimCorrectiveAction(orm.Model):
    _name = 'crm.claim.corrective.action'

    _columns = {
        'name': fields.text('Name', size=256, required=True),
        'sequence': fields.integer('Sequence'),
        'sol_claim_id': fields.many2one('crm.claim', 'Claim',
                                        help='Select a CRM Claim'),
        'responsible_id': fields.many2one('res.users', 'Responsible',
                                          help='Select a Responsible'),
        'date_planned': fields.date('Planned Date'),
        'date_done': fields.date('Date Done'),
        'corrective_action_id': fields.many2one('crm.claim.corrective',
                                                'Corrective action'),
    }

    def create(self, cr, uid, vals, context=None):
        if vals.get('corrective_action_id') and not vals.get('sol_claim_id'):
            correct_obj = self.pool['crm.claim.corrective']
            claim = correct_obj.read(cr, uid, vals['corrective_action_id'],
                                     ['claim_id'], context=context)
            claim_id = claim and claim['claim_id'] and claim['claim_id'][0]
            if claim_id:
                vals['sol_claim_id'] = claim_id
        return super(CrmClaimCorrectiveAction, self).create(cr, uid, vals,
                                                            context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if 'corrective_action_id' in vals and vals['corrective_action_id']:
            correct_obj = self.pool['crm.claim.corrective']
            claim = correct_obj.read(cr, uid, vals['corrective_action_id'],
                                     ['claim_id'], context=context)
            claim_id = claim and claim['claim_id'] and claim['claim_id'][0]
            if claim_id:
                vals['sol_claim_id'] = claim_id
        return super(CrmClaimCorrectiveAction, self).write(cr, uid, ids, vals,
                                                           context=context)
