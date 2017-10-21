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
import logging

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = "hr.employee"
    _description = "Employee"

    employee_bonus_ids = fields.One2many('employee.bonus',
                                         'employee_id',
                                         string='Bonus')

    fixed_bonus = fields.Float(string='Brutto Base Bonus')
    final_fixed_bonus = fields.Float(string='Netto Base Bonus')
    calculate_bonus = fields.Float(string='Brutto Salary Bonus')
    final_calculate_bonus = fields.Float(string='Netto Salary Bonus')
    other_bonus = fields.Float(string='Customer Bonus')
    total_bonus = fields.Float(string='Netto Total Bonus')

    shared_profit = fields.Float(string='Shared Profit')
    user_wage = fields.Float(string='User Wage')
    all_wage = fields.Float(string='All Wage')

    all_work_days = fields.Integer(string='Work Days All Time')
    work_days = fields.Integer(string='Work Days This Year')
    tax_free = fields.Boolean(string='Tax Free',
                              default=False)
