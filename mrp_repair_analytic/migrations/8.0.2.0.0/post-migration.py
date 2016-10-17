# -*- coding: utf-8 -*-
# © 2016 Esther Martín - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def update_repair_id(cr):
    cr.execute(
        """
        UPDATE account_analytic_line SET repair_id = rep_data.id
        FROM (
            SELECT id, analytic_account as account
            FROM mrp_repair
        ) as rep_data
        WHERE account_analytic_line.account_id = account
        """
    )


def migrate(cr, version):
    if not version:
        return
    update_repair_id(cr)
