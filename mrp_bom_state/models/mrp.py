# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    _track = {
        'state': {
            'mrp_bom_version.mt_active': lambda self, cr, uid, obj,
            ctx=None: obj.state == 'active',
        },
    }

    def _get_max_sequence(self):
        bom = self.search([], order='sequence desc', limit=1)
        maxseq = bom.sequence + 1
        return maxseq

    active = fields.Boolean(
        string='Active', default=False, readonly=True,
        states={'draft': [('readonly', False)]})
    historical_date = fields.Date(string='Historical Date', readonly=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('active', 'Active'),
                              ('historical', 'Historical'),
                              ], string='Status', index=True, readonly=True,
                             default='draft', copy=False)
    product_tmpl_id = fields.Many2one(
        readonly=True, states={'draft': [('readonly', False)]})
    product_id = fields.Many2one(
        readonly=True, states={'draft': [('readonly', False)]})
    product_qty = fields.Float(
        readonly=True, states={'draft': [('readonly', False)]})
    sequence = fields.Integer(
        default=_get_max_sequence, copy=False,
        states={'historical': [('readonly', True)]})
    name = fields.Char(
        states={'historical': [('readonly', True)]})
    code = fields.Char(
        states={'historical': [('readonly', True)]})
    type = fields.Selection(
        states={'historical': [('readonly', True)]})
    company_id = fields.Many2one(
        states={'historical': [('readonly', True)]})
    product_uom = fields.Many2one(
        states={'historical': [('readonly', True)]})
    routing_id = fields.Many2one(
        readonly=True, states={'draft': [('readonly', False)]})
    bom_line_ids = fields.One2many(
        readonly=True, states={'draft': [('readonly', False)]})
    position = fields.Char(
        states={'historical': [('readonly', True)]})
    date_start = fields.Date(
        states={'historical': [('readonly', True)]})
    date_stop = fields.Date(
        states={'historical': [('readonly', True)]})
    property_ids = fields.Many2many(
        states={'historical': [('readonly', True)]})
    product_rounding = fields.Float(
        states={'historical': [('readonly', True)]})
    product_efficiency = fields.Float(
        states={'historical': [('readonly', True)]})
    message_follower_ids = fields.Many2many(
        states={'historical': [('readonly', True)]})
    message_ids = fields.One2many(
        states={'historical': [('readonly', True)]})

    @api.one
    @api.constrains('sequence')
    def check_mrp_bom_sequence(self):
        domain = [('id', '!=', self.id), ('sequence', '=', self.sequence),
                  ('product_tmpl_id', '=', self.product_tmpl_id.id),
                  ('product_id', '=', self.product_id.id)]
        if self.search(domain):
            raise exceptions.Warning(
                _('The sequence must be unique'))

    @api.one
    def copy(self, default=None):
        bom = self.search([], order='sequence desc', limit=1)
        maxseq = bom.sequence + 1
        default.update({'sequence': maxseq})
        return super(MrpBom, self).copy(default=default)

    @api.multi
    def button_draft(self):
        self.state = 'draft'

    @api.multi
    def button_activate(self):
        self.ensure_one()
        if self.routing_id:
            return self.write({'active': True,
                               'state': 'active'})
        context = self.env.context.copy()
        context['active_id'] = self.id
        context['active_ids'] = [self.id]
        context['active_model'] = 'mrp.bom'
        return {'name': _('Confirm activation'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wiz.confirm.activation',
                'target': 'new',
                'context': context,
                }

    @api.multi
    def button_historical(self):
        context = self.env.context.copy()
        context['active_id'] = self.id
        context['active_ids'] = [self.id]
        context['active_model'] = 'mrp.bom'
        return {'name': _('Confirm historification'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wiz.confirm.historification',
                'target': 'new',
                'context': context,
                }


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def product_id_change(self, cr, uid, ids, product_id, product_qty=0,
                          context=None):
        bom_obj = self.pool['mrp.bom']
        product_obj = self.pool['product.product']
        res = super(MrpProduction, self).product_id_change(
            cr, uid, ids, product_id=product_id, product_qty=product_qty,
            context=context)
        if product_id:
            res['value'].update({'bom_id': False})
            product_tmpl_id = product_obj.browse(
                cr, uid, product_id, context=context).product_tmpl_id.id
            domain = [('state', '=', 'active'),
                      '|',
                      ('product_id', '=', product_id),
                      '&',
                      ('product_id', '=', False),
                      ('product_tmpl_id', '=', product_tmpl_id)
                      ]
            domain = domain + ['|', ('date_start', '=', False),
                               ('date_start', '<=', fields.Datetime.now()),
                               '|', ('date_stop', '=', False),
                               ('date_stop', '>=', fields.Datetime.now())]
            bom_ids = bom_obj.search(cr, uid, domain, context=context)
            bom_id = 0
            min_seq = 0
            for bom in bom_obj.browse(cr, uid, bom_ids, context=context):
                if min_seq == 0 or bom.sequence < min_seq:
                    min_seq = bom.sequence
                    bom_id = bom.id
            if bom_id > 0:
                res['value'].update({'bom_id': bom_id})
        return res
