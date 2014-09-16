# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

{
    "name": "Purchase Requisition Order Generator",
    "version": "1.0",
    "depends": [
        "purchase_requisition",
    ],
    "author": "OdooMRP team",
    "contributors": [
        "Alfredo de la Fuente <alfredodelafuente@avanzosc.es>",
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
    ],
    "category": "Purchase Management",
    "website": "http://www.odoomrp.com",
    "summary": "",
    "description": """
While standard module allows to create a purchase order for one partner each
time, this module allows to create purchase orders for all registered suppliers
in product information clicking a button
    """,
    "data": [
        "views/purchase_requisition_view.xml",
    ],
    "installable": True,
}
