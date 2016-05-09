# -*- coding: utf-8 -*-
# © 2014-2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def assign_product_template(cr, registry):
    """This post-init-hook will update all existing mrp.bom.line,
        mrp.production and mrp.production.product.line"""
    cr.execute("""
        UPDATE mrp_bom_line AS line
        SET product_tmpl_id = product_product.product_tmpl_id
        FROM product_product
        WHERE line.product_id = product_product.id;""")
    cr.execute("""
        UPDATE mrp_production AS line
        SET product_tmpl_id = product_product.product_tmpl_id
        FROM product_product
        WHERE line.product_id = product_product.id;""")
    cr.execute("""
        UPDATE mrp_production_product_line AS line
        SET product_tmpl_id = product_product.product_tmpl_id
        FROM product_product
        WHERE line.product_id = product_product.id;""")
