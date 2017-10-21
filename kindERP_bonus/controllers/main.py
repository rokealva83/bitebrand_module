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

import odoo
from odoo import http, api
from odoo.http import request


class Website(odoo.addons.web.controllers.main.Home):
    @http.route('/employee_bonus', type='http', auth="user", website=True)
    def employee_bonus(self, **kw):

        hr_employee_pool = request.env['hr.employee']
        hr_employee = hr_employee_pool.search(
            [('user_id', '=', request.env.uid)])
        employee_bonus = 0
        for employee_bonus_id in hr_employee.employee_bonus_ids:
            employee_bonus += employee_bonus_id.bonus
        value = {
            'shared_profit': hr_employee.shared_profit,
            'final_fixed_bonus': hr_employee.final_fixed_bonus,
            'final_calculate_bonus': hr_employee.final_calculate_bonus,
            'employee_bonus': employee_bonus,
            'total_bonus':  hr_employee.total_bonus,
            'link': '/web'
        }
        return request.website.render("website.bonus_page", value)
