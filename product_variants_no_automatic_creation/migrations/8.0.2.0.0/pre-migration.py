# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    if not version:
        return
    cr.execute("""
        UPDATE ir_model_data
        SET module='product_variants_no_automatic_creation'
        WHERE name='group_product_variant_extended_description';""")
    cr.execute("""
        DELETE FROM ir_ui_view
        WHERE name='sale settings (for product variants)';""")
