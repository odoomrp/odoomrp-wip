# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def update_mrp_workcenter(cr):
    cr.execute(
        """
        UPDATE mrp_workcenter
           SET capacity_per_cycle_min = 1.0
         WHERE capacity_per_cycle_min = 0.0
        """)
    cr.execute(
        """
        UPDATE mrp_workcenter
           SET capacity_per_cycle = 1.0
         WHERE capacity_per_cycle = 0.0
        """)


def migrate(cr, version):
    if not version:
        return
    update_mrp_workcenter(cr)
