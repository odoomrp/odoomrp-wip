# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def update_sale_order_lines(cr):
    cr.execute(
        """
        ALTER TABLE sale_order_line
        RENAME COLUMN product_template TO product_tmpl_id;
        """)
    cr.execute(
        """
        INSERT INTO product_configurator_attribute
            (owner_model, owner_id, attribute_id, value_id, product_tmpl_id)
        SELECT
            'sale.order.line',
            sale_line,
            attribute_id,
            value_id,
            product_tmpl_id
        FROM
            sale_order_line_attribute AS attr,
            sale_order_line AS line
        WHERE
            line.id = attr.sale_line
            AND sale_line IS NOT NULL;
        """)


def migrate(cr, version):
    if not version:
        return
    update_sale_order_lines(cr)
