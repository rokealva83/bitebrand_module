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
    'name': 'kindERP Events',
    'version': '1.0',
    'author': 'Libre Comunication',
    'category': 'kindERP',

    'description': """
        """,

    'depends': [
        'event',
    ],

    'data': [
        'views/event_views.xml',
        'views/slack_settings_views.xml',
        'views/event_registration_template.xml',
        'views/private_email_template.xml',

        'security/ir.model.access.csv',

        # 'wizard/create_message.xml',
    ],

    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
    'application': True,

    'js': ['static/js/form_widgets.js'],
    'qweb': ['static//xml/base.xml'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
