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


class HrHolidaysConfiguration(models.Model):
    _name = "hr.holidays.configuration"
    _description = "Holiday Configuration"

    name = fields.Char(string="Name")
    minimum_month_work = fields.Integer(string="Minimum Month Work")
    vacation = fields.Integer(string="Vacation")
    vac_day_per_month = fields.Float(string="Vacation Day Per Month")
    sick_leave = fields.Integer(string="Sick Leave")
    day_off = fields.Integer(string="Day Off")
    unlimited_day_off = fields.Boolean(string="Day Off Unlimited")
    save_vacation = fields.Boolean(string="Save Vacation")
