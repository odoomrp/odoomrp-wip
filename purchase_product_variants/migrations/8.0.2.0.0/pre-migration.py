# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openupgradelib import openupgrade


def update_purchase_order_lines(cr):
    cr.execute("""
        ALTER TABLE purchase_order_line
        RENAME COLUMN product_template TO product_tmpl_id;
        """)
    if openupgrade.column_exists(
            cr, 'purchase_order_line_attribute', 'attribute_id'):
        attribute_column = 'attribute_id'
        value_column = 'value_id'
    else:
        attribute_column = 'attribute'
        value_column = 'value'
    cr.execute("""
        INSERT INTO product_configurator_attribute
            (owner_model, owner_id, attribute_id, value_id, product_tmpl_id)
        SELECT
            'purchase.order.line',
            attr.purchase_line,
            attr.%s,
            attr.%s,
            line.product_tmpl_id
        FROM
            purchase_order_line_attribute AS attr,
            purchase_order_line AS line
        WHERE
            line.id = attr.purchase_line
            AND attr.purchase_line IS NOT NULL;
        """ % (attribute_column, value_column))


def migrate(cr, version):
    if not version:
        return
    update_purchase_order_lines(cr)
