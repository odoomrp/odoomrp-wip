
{
    'name': 'Stock Move Check Availability',
    'version': '1.0',
    'description': """
    This module adds a button to check availability in stock moves.
    """,
    'author': 'OdooMRP team',
    'website': 'http://www.odoomrp.com',
    "depends": ['stock'],
    "category": "Generic Modules",
    "data": ['views/stock_move_view.xml'
             ],
    "installable": True,
}
