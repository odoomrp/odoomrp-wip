# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'

    lot_default_locked = fields.Boolean(
        string='Block new Serial Numbers/lots',
        help='If checked, future Serial Numbers/lots will be created blocked '
             'by default')

    def _get_parent_default_locked(self):
        """Locked (including categories)

        @return True when the category or one of the parents demand new lots
                to be locked"""
        _locked = self.lot_default_locked
        categ = self.parent_id
        while categ and not _locked:
            _locked = categ.lot_default_locked
            categ = categ.parent_id
        return _locked
