# -*- coding: utf-8 -*-
{
    'name': "hr_ldap_sync",

    'summary': """User, HR Employees, companies and departments synchronization with LDAP""",

    'description': """
        LDAP usualy holds all the necessary info about a company hierachical employee structure. This module aims to load that structure
        to Odoo and maintain it synced.
    """,

    'author': "Decsis",
    'website': "https://www.decsis.eu",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'hr',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr','auth_ldap'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}