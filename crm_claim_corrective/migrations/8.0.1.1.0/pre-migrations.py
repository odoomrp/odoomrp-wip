# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def update_fieldname(cr):
    cr.execute(
        """
        ALTER TABLE crm_claim
        RENAME COLUMN aaccseq TO corrective_id;
        """)
    cr.execute(
        """
        ALTER TABLE crm_claim
        RENAME COLUMN desc_decis TO decision_desc;
        """)
    cr.execute(
        """
        ALTER TABLE crm_claim
        RENAME COLUMN desc_cause TO cause_desc;
        """)
    cr.execute(
        """
        ALTER TABLE crm_claim
        RENAME COLUMN nfdecision_id TO ncdecision_id;
        """)
    cr.execute(
        """
        ALTER TABLE crm_claim
        RENAME COLUMN nfdesc_decis TO ncdecision_desc;
        """)
    cr.execute(
        """
        ALTER TABLE crm_claim_corrective
        RENAME COLUMN seq TO code;
        """)
    cr.execute(
        """
        ALTER TABLE crm_claim_corrective_action
        ALTER COLUMN name TYPE varchar;
        """)
    cr.execute(
        """
        ALTER TABLE crm_claim_corrective_action
        RENAME COLUMN corrective_action_id TO corrective_id;
        """)
    cr.execute(
        """
        ALTER TABLE crm_claim_problem_description
        ALTER COLUMN name TYPE varchar
        """)
    cr.execute(
        """
        ALTER TABLE crm_claim_problem_cause
        ALTER COLUMN name TYPE varchar
        """)
    cr.execute(
        """
        ALTER TABLE crm_claim_problem_solution
        ALTER COLUMN name TYPE varchar
        """)
    cr.execute(
        """
        ALTER TABLE crm_claim_decision
        ALTER COLUMN name TYPE varchar
        """)


def migrate(cr, version):
    if not version:
        return
    update_fieldname(cr)
