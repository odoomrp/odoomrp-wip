# -*- coding: utf-8 -*-
# © 2014-2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def assign_product_template(cr, registry):
    """This post-init-hook will update all existing sale.order.line"""
    cr.execute(
        """
        SELECT count(attname) FROM pg_attribute
        WHERE attrelid =
          (SELECT oid FROM pg_class WHERE relname = %s)
          AND attname = %s""",
        ('sale_order_line', 'product_tmpl_id'))
    if not cr.fetchone()[0] == 1:
        cr.execute("""
            ALTER TABLE sale_order_line
            ADD COLUMN product_tmpl_id integer;""")
    cr.execute("""
        UPDATE sale_order_line AS line
        SET product_tmpl_id = product_product.product_tmpl_id
        FROM product_product
        WHERE line.product_id = product_product.id;""")
