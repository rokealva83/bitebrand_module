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
    'name': 'kindERP fields',
    'version': '1.0',
    'author': 'Libre Comunication',
    'category': 'kindERP',

    'description': """
        This module is based on module - Employee Directory

        New functionality added:
            - Saving additional files of the employee (passport scan, CV, etc..)
            - Equipment tracking features

        Fields that was added:
          Required:
            - Personal email
            - Skype

          Not required:
            - First Name
            - Second Name
            - Last Name
            - Contract No
            - Key Card No
            - Secondary phone
            - Jira
            - BitBucket
            - GitHub
            - Gitlab

          This fields attributes set as required:
            - working address
            - work mobile
            - Gender
            - Date of Birth
        """,

    'depends': [
        'website',
        'hr',
        'hr_contract',
    ],

    'data': [
        'security/ir.model.access.csv',
        'security/security_date.xml',

        'wizard/wizard_view.xml',

        'views/hr_view.xml',
        'views/equipment_views.xml',
        'views/logo_view.xml'
    ],

    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
