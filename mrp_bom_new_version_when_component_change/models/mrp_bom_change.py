# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, exceptions, _


class MrpBomChange(models.Model):
    _inherit = 'mrp.bom.change'

    @api.one
    def do_component_change(self):
        if not self.old_component or not self.new_component:
            raise exceptions.Warning(_("Not Components selected!"))
        if not self.boms:
            raise exceptions.Warning(_("There isn't any BoM for selected "
                                       "component"))
        bom_ids = []
        for bom in self.boms:
            change_bom = False
            for bom_line in bom.bom_line_ids:
                if bom_line.product_id.id == self.old_component.id:
                    change_bom = True
                    break
            if not change_bom:
                bom_ids.append(bom.id)
            else:
                new_bom = bom._copy_bom()
                bom._update_bom_state_after_copy()
                new_bom.button_activate()
                bom_ids.append(new_bom.id)
        self.boms = [(6, 0, bom_ids)]
        super(MrpBomChange, self).do_component_change()
