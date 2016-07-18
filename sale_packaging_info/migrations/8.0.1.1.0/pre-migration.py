# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def update_columns(cr):
    cr.execute(
        """
        ALTER TABLE sale_order
        RENAME COLUMN product_ul TO product_ul_id
        """)
    cr.execute(
        """
        ALTER TABLE sale_order_line
        RENAME COLUMN sec_pack TO sec_pack_id
        """)


def migrate(cr, version):
    if not version:
        return
    update_columns(cr)
