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
    "name": "MRP Production Project Estimated Cost",
    "version": "1.0",
    "author": "OdooMRP team",
    "category": "MRP",
    "website": "http://www.odoomrp.com",
    "description": """
    With this module when you confirm one production order, analytical notes
    are automatically generated with the estimated costs of the production
    order.

    This module performs the following:

    1.- In 'account.analytic.line' object, fields have been added:
        1.1.- Estimate Standard Cost of the product.
        1.2.- Estimate Average Cost of the product.
        1.3.- Last Purchase Cost of the product.
        1.4.- Last Sale Price of the product.

    2.- In 'product.template' object, field have been added::
        2.1.- Manual Standard Cost.

    3.- Creates three analytical journals, are these:
        3.1.- Estimated materials.
        3.2.- Estimated operators.
        3.3.- Estimated machines.

    When the production order is confirmed, the estimated allocation of
    materials, machinery operators and costs will be made.

    4.- For the estimated imputation of materials, for each material to
        consume of the order, a line of analytical will be created with this
        values​​:
        4.01.- Description: CodOF-CodOp-CodProduct
        4.02.- Analytic Account/Project:.That of the production order.
        4.03.- Analytic Journal: Estimated materials journal.
        4.04.- User: User confirming the production order.
        4.05.- Invoiceable: False.
        4.06.- Date: Date of the imputation.
        4.07.- Amount: Cero
        4.08.- Product: Product to consume.
        4.09.- Quantity: Amount of line material to consume in production
                         order.
        4.10.- General Account: Account associated with the product or
                                category.
        4.11.- Estimate Standard Cost: The value that show the product.
        4.12.- Manual Standard Cost: The value that show the product.
        4.13.- Last Purchase Cost: The value that show the product.
        4.14.- Last Sale Price: The value that show the product.

    5.- For estimated imputation of operators, for each operation, a line of
        analytical will be created with this values​​:
        5.01.- Description: CodOF-CodOp-CodProduct
        5.02.- Analytic Account/Project:.That of the production order.
        5.03.- Analytic Journal: Estimated operators journal.
        5.04.- User: User confirming the production order.
        5.05.- Invoiceable: False.
        5.06.- Date: Date of the imputation.
        5.07.- Amount: Cero
        5.08.- Product: Product associated with the machine in operation.
        5.09.- Quantity: Amount of time required for the execution of the
                         operation.
        5.10.- General Account: Account associated with the product or
                                category.
        5.11.- Estimate Standard Cost: The value that show the product.
        5.12.- Manual Standard Cost: The value that show the product.
        5.13.- Last Purchase Cost: The value that show the product.
        5.14.- Last Sale Price: The value that show the product.

        The number of imputations of workers is equal to defined number of
        operators in the operation

    6.- For the estimated imputation of machines, for each operation on the
        route associated, 2 imputations are made, per cost hour, and per cost
        per cycle. will be created with this values​​:
        6.01.- Description: CodOF-CodOp-H-Machinename or
                            CodOF-CodOp-C-Machinename.
        6.02.- Analytic Account/Project:.That of the production order.
        6.03.- Analytic Journal: Estimated machines journal.
        6.04.- User: User confirming the production order.
        6.05.- Invoiceable: False.
        6.06.- Date: Date of the imputation.
        6.07.- Amount: Cero
        6.08.- Product: Product associated with the machine in operation.
        6.09.- Quantity: Expected amount of time or cycles to perform the
                         operation.
        6.10.- General Account: Account associated with the product or
                                category.
        6.11.- Estimate Standard Cost: The value that show the product.
        6.12.- Manual Standard Cost: The value that show the product.
        6.13.- Last Purchase Cost: The value that show the product.
        6.14.- Last Sale Price: The value that show the product.
    """,
    "depends": ['product',
                'analytic',
                'mrp',
                'mrp_operations_extension',
                'mrp_project_link',
                'product_last_price_info',
                ],
    "data": ['data/analytic_journal_data.xml',
             'views/account_analytic_line_view.xml',
             'views/product_view.xml',
             ],
    "installable": True
}
