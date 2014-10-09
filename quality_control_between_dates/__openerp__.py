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
    "name": "Quality Control Between Dates",
    "version": "1.0",
    "author": "OdooMRP team",
    "category": "MRP",
    "website": "http://www.odoomrp.com",
    "description": """
    This module performs the following:

    1.- Created two new fields in the test template line:

        1.1.- Validity Start Date, required.
        1.2.- Validity End Date.

    Before creating a new object in test template line, it will validate that
    there is no previous line without Validity End Date, for the new test
    template line you want to create.

    When a new test line is created from a template, will validate that the
    date on which this object is created, is between the new dates of the
    Test Template Line.
    """,
    "depends": ['quality_control',
                ],
    "data": ['views/qc_test_template_line_view.xml',
             ],
    "installable": True
}
