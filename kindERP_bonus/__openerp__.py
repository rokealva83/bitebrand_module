# -*- coding: UTF-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016-Today Libre Comunication (<erpsystem.com.ua@gmail.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'kindERP Bonus System',
    'version': '1.0',
    'author': 'Libre Comunication',
    'category': 'kindERP',

    'description': """
        """,

    'depends': [
        'hr',
        'kindERP_fields',
        'kindERP_invoicing'
    ],

    'data': [
        'views/bonus_settings_views.xml',
        'views/hr_view.xml',
        'views/hr_contract_view.xml',
        'views/res_partner_views.xml',
        'views/salary_system_views.xml',

        'web/bonus_page.xml',

        'data/bonus_data.xml',

        'security/ir.model.access.csv',
    ],

    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
    'application': True,

    'js': ['static/js/form_widgets.js'],
    'qweb': ['static//xml/base.xml', ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
