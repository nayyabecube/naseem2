# -*- coding: utf-8 -*-
{
    'name': "cheque_book_maintaines",

    'summary': """
        Nayyab""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        'views/cheque_book_view.xml',
        'views/res_bank_view.xml',
        'views/res_users_view.xml',
        'views/account_account_view.xml',
        'views/account_move_view.xml',
        'views/bank_transfer_view.xml',
        'views/customer_adjustments_view.xml',
        'views/supp_adjustments_view.xml',
        'views/menu_items.xml',
    ],

}