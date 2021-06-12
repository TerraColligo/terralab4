# -*- coding: utf-8 -*-
{
    'name': "TerraLab LANISAF",

    'summary': """
        TerraLab LANISAF customizations""",

    'description': """
        TerraLab LANISAF customizations.
    """,

    'author': "TerraLab Oy",
    'website': "https://www.terralab.fi",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    # Fixed version syntax. Odoo add-ons versions scheme must be major odoo version.x.x.x for Odoo to detect changes in modules and apply updates. In this case 13.x.x.x.
    'category': 'Specific Industry Applications',
    'version': '13.0.2.47',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'sale', 'google_spreadsheet', 'uom', 'mrp', 'stock', 'sale_management', 'terralab'],

    # always loaded; these need to be in a specific order
    'data': [
        'reports/lanisaf/order_confirmation_document.xml',
        'reports/lanisaf/order_confirmation.xml',
        'reports/lanisaf/test_results.xml',
        'reports/lanisaf/test_results_document.xml',
    ],
    'css': [
        'static/src/css/terralab-lanisaf.css',
    ],
    'images': [
        'static/images/dicea-logo.png',
        'static/images/lanisaf-logo.png',
        'static/images/escudo-uach-logo.jpg',
        'static/images/lanisaf-icon.jpg',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'application': True,

    # PIP requirements - install with pip3 install
    'external_dependencies': {
        'python': [],
    },
}
