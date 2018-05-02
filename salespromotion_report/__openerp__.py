# -*- coding: utf-8 -*-
{
    'name': "salespromotion_report",

    'summary': "salespromotion_report",

    'description': "salespromotion_report",

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
