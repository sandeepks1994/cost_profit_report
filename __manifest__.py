# -*- coding: utf-8 -*-

##############################################################################
#
#    Author: Al Kidhma
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <https://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Cost Profit Report',
    'version': '13.0',
    'category': 'Generic Modules/Others',
    'sequence': 2,
    'summary': 'Cost Profit and Income Report',
    'description': """
Sales Reports
    """,
    'author': 'Al Kidhma',
    'depends': ['sale_management', 'account'],
    'data': [
        'reports/report.xml',
        'reports/report_income_procedure_profit.xml',
        'wizard/income_procedure_profit.xml',
        'views/report.xml',
        'views/sales_report.xml',
        'views/sales_report_wizard.xml',
            ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
