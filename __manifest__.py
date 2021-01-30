# -*- encoding: utf-8 -*-
{

    'name': 'Income by Procedure Report(Income,Cost,Profit)',
    'version': '11.0',
    'author': 'Al Khidma Systems',
    'sequence': 2,
    'category': '',
    'depends': ['sale'],
    'description': """

""",
    'website': 'http://www.alkhidmasystems.com',
    "data": [
        'reports/report.xml',
        'wizard/income_procedure_profit.xml',
        'reports/report_income_procedure_profit.xml',
        'views/report.xml',
        'views/sales_report.xml',
        'views/sales_report_wizard.xml',
            ],
    'active': False,
    'images': [],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
