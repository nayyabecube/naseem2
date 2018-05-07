# -*- coding: utf-8 -*-
{
    'name': "customer_last_transaction",

    'summary': "customer_last_transaction",

    'description': "customer_last_transaction",

    'author': "Rana Rizwan",
    'website': "http://www.bcube.com",

    # any module necessary for this one to work correctly
    'depends': ['base'],
    # always loaded
    'data': [
        'template.xml',
        'views/module_report.xml',
    ],
    'css': ['static/src/css/report.css'],
}
