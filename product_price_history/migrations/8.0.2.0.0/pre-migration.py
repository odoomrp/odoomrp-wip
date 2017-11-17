# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def update_history(cr):
    cr.execute("""
        ALTER TABLE product_price_history
        RENAME COLUMN product TO product_id;
        """)


def migrate(cr, version):
    if not version:
        return
    update_history(cr)
