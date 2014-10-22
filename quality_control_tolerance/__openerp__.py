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
    "name": "Quality Control Tolerance",
    "version": "1.0",
    "author": "OdooMRP team",
    "category": "Generic Modules/Others",
    "website": "http://www.odoomrp.com",
    "description": """
    This module performs the following:

    1.- New selection field in quality test called 'Tolerance status', with the
        following possible values: Optima, Tolerable, Admissible, No
        Admissible.

    2.- In test template line, two new fields:
        2.1.- % Optimal Admissible Tolerance.
        2.2.- % Variable Tolerance.

    With this, the standard range (min-max) is extended with tolerances, having
    these control ranges:
    1.- NOT ADMISSIBLE. In color red, tolerance status 'No Admissible'.
    2.- min allowed. In Color orange, tolerance status 'Admissible'.
    3.- variable min. In color blue, tolerance status 'Tolerable.
    4.- min ---- test in range --- max. In color green, tolerance status
        'Optima'.
    5.- max variable. In Color blue, , tolerance status 'Tolerable.
    6.- allowed max. In Color orange, tolerance status 'Admissible'.
    7.- NOT ADMISSIBLE. In Color red, tolerance status 'No Admissible'.

    If a value of fest is NOT admissible -> Value Combo: NO admissible and line
    color RED.
    If a value is in allowed min or max -> Value Combo: admissible and line
    color ORANGE.
    If a value is in variable min or max -> Value Combo: tolerable and line
    color BLUE.
    If a value is between the range min and max -> Value Combo: optimal and
    line color GREEN.

    Values ​​OK / NOK line:
    1.- If less allowed min, or is greater than allowed max, the line is
        not ok.
    2.- If it is within allowed, is up to the user to indicate whether pass
        or fail.
    3.- Between min and max variable, the value of the test line would OK but
        the operator may change.
    4.- If it is within range min and max, The value of test line would be OK.

    Extensive functionality calculating OK / NOK standard test to consider the
    2 new fields%% optimal tolerance and permissible tolerance template, and
    associate the corresponding value of the color combo and the line to assess
    the value.
    """,
    "depends": ['quality_control',
                ],
    "data": ['views/qc_test_view.xml',
             ],
    "installable": True
}
