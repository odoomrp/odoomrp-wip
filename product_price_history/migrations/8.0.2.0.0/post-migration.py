# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def update_history(cr):
    cr.execute("""
        INSERT INTO product_price_history_product
            (create_uid,
             create_date,
             write_uid,
             write_date,
             datetime,
             product_id,
             product_template_id,
             cost,
             company_id)
        SELECT
            create_uid,
            create_date,
            write_uid,
            write_date,
            datetime,
            product_id,
            product_template_id,
            cost,
            company_id
           FROM
            product_price_history
        WHERE product_id IS NOT NULL;
        """)
    cr.execute("""
        DELETE FROM product_price_history
        WHERE product_id IS NOT NULL;
        """)
    cr.execute("""
        ALTER TABLE product_price_history
        DROP COLUMN product_id;
        """)


def migrate(cr, version):
    if not version:
        return
    update_history(cr)
