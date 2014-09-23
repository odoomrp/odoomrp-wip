# -*- encoding: utf-8 -*-
##############################################################################
#
#    Avanzosc - Avanced Open Source Consulting
#    Copyright (C) 2011 - 2014 Avanzosc <http://www.avanzosc.com>
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
    "name": "Produtc Catch Suppliers From Category",
    "version": "1.0",
    "author": "AvanzOSC",
    "category": "Product",
    "website": "www.avanzosc.es",
    "description": """
    This module allows you to assign suppliers in one category.
    When you assing a category to one product, automatically assigns the
    suppliers from the category, to the product.
    """,
    "depends": [
        'base',
        'product',
    ],
    "data": ['views/product_category_view.xml',
             'views/product_view.xml',
             ],
    "installable": True
}
