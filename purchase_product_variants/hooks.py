# -*- coding: utf-8 -*-
# © 2014-2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def assign_product_template(cr, registry):
    """This post-init-hook will update all existing purchase.order.line"""
    cr.execute("""
        UPDATE purchase_order_line AS line
        SET product_tmpl_id = product_product.product_tmpl_id
        FROM product_product
        WHERE line.product_id = product_product.id;""")
