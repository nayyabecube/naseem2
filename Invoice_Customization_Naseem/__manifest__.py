# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Invoice Customization Naseem',
    'author': 'BCUBE',
    'summary': 'Invoice Customization Naseem',
    'website': 'bcube.pk',
    'version': '10',
    'depends': ['product','account','purchase','stock','stock_account'],
    'data': [
        'views/sale_naseem.xml',
        'views/account_invoice_naseem.xml',
        'views/stock_naseem.xml',
        'views/transport_info.xml',
    ],
    'css': ['static/src/css/my_css.css'],
    'installable': True,
    'auto_install': False
}
