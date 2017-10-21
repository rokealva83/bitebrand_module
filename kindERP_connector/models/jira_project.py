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

from odoo import models, fields, api, _


class JiraProject(models.Model):
    _name = "jira.project"

    key = fields.Char(string='JIRA key',
                      size=256)
    name = fields.Char(string='JIRA project name',
                       size=256)

    _sql_constraints = [
        ('key_uniq', 'unique (key)', 'The JIRA key must be unique !'),
    ]


class JiraProjectConf(models.Model):
    _name = "jira.project.conf"

    name = fields.Char(string='JIRA User Name',
                       size=256)
    user_id = fields.Many2one('res.users',
                              string='User')
    password = fields.Char('JIRA Password',
                           size=256)
    product_id = fields.Many2one('product.product',
                                 string='Product')
