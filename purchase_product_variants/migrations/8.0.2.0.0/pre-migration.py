# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def update_purchase_order_lines(cr):
    cr.execute("""
        ALTER TABLE purchase_order_line
        RENAME COLUMN product_template TO product_tmpl_id;
        """)
    cr.execute("""
        INSERT INTO product_configurator_attribute
            (owner_model, owner_id, attribute_id, value_id, product_tmpl_id)
        SELECT
            'purchase.order.line',
            attr.purchase_line,
            attr.attribute_id,
            attr.value_id,
            line.product_tmpl_id
        FROM
            purchase_order_line_attribute AS attr,
            purchase_order_line AS line
        WHERE
            line.id = attr.purchase_line
            AND attr.purchase_line IS NOT NULL;
        """)


def migrate(cr, version):
    if not version:
        return
    update_purchase_order_lines(cr)
