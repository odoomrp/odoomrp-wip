# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def update_column_names(cr):
    cr.execute("""
        ALTER TABLE mrp_bom_line
        RENAME COLUMN product_template TO product_tmpl_id;
        """)
    cr.execute("""
        ALTER TABLE mrp_production
        RENAME COLUMN product_template TO product_tmpl_id;
        """)
    cr.execute("""
        INSERT INTO product_configurator_attribute
            (owner_model, owner_id, attribute_id, value_id, product_tmpl_id)
        SELECT
            'mrp.production',
            attr.mrp_production,
            attr.attribute,
            attr.value,
            line.product_tmpl_id
        FROM
            mrp_production_attribute AS attr,
            mrp_production AS line
        WHERE
            line.id = attr.mrp_production
            AND attr.mrp_production IS NOT NULL;
        """)
    cr.execute("""
        ALTER TABLE mrp_production_product_line
        RENAME COLUMN product_template TO product_tmpl_id;
        """)
    cr.execute("""
        INSERT INTO product_configurator_attribute
            (owner_model, owner_id, attribute_id, value_id, product_tmpl_id)
        SELECT
            'mrp.production.product.line',
            attr.product_line,
            attr.attribute,
            attr.value,
            line.product_tmpl_id
        FROM
            mrp_production_product_line_attribute AS attr,
            mrp_production_product_line AS line
        WHERE
            line.id = attr.product_line
            AND attr.product_line IS NOT NULL;
        """)


def migrate(cr, version):
    if not version:
        return
    update_column_names(cr)
