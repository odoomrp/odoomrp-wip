
{
    'name': 'Machine Purchase Asset',
    'version': '1.0',
    'description': """
    This module links assets with machines if the created product asset is a
    machine.
    """,
    'author': 'OdooMRP team',
    'website': 'http://www.odoomrp.com',
    "depends": ['machine_purchase', 'account_asset'],
    "category": "Generic Modules",
    "data": ['views/machinery_view.xml',
             ],
    "installable": True,
    "auto_install": True,
}
