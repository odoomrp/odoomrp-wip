# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, SUPERUSER_ID


def update_descriptions(cr):
    cr.execute(
        """
        UPDATE crm_claim_corrective
        SET name = code WHERE name IS NULL;
        """)
    cr.execute(
        """
        UPDATE crm_claim_corrective
        SET code = '/' WHERE code NOT ILIKE '/';
        """)
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        env.ref('crm_claim_corrective.crm_claim_corrective_seq').write(
            {'number_next_actual': 1})
        correctives = env['crm.claim.corrective'].search([('code', '=', '/')])
        for corrective in correctives:
            corrective.write({
                'code': env['ir.sequence'].get('crm.claim.corrective'),
            })


def migrate(cr, version):
    if not version:
        return
    update_descriptions(cr)
