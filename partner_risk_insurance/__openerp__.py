# -*- encoding: utf-8 -*-
{
    "name": "Partner Risk Insurance",
    "version": "0.1",
    "description": """
    This module adds a new tab in the partner form to introduce risk insurance
     information.
    --Module of nan-tic nan_partner_insurance ported by Factor Libre to
     OpenERP 7
""",
    "author": "Factor Libre S.L, NaN·tic",
    "website": "http://www.factorlibre.com",
    "depends": [
        'base',
    ],
    "category": "Custom Modules",
    "data": [
        'partner_view.xml',
    ],
    "active": False,
    "installable": True
}
