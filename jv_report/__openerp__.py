# -*- coding: utf-8 -*-
{
    'name': "jv_report",

    'summary': "jv_report",

    'description': "jv_report",

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
