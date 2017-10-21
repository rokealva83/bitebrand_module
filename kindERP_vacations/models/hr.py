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
from datetime import date, datetime, timedelta
import calendar


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.multi
    def _get_employee_time_work(self):
        if len(self) == 1:
            is_worker = False

            if self.contract_ids:
                last_work_day = self.contract_ids[-1].date_end
                if last_work_day:
                    last_work_day = datetime.strptime(
                        last_work_day.replace('-', ''), "%Y%m%d").date()
                    if last_work_day >= date.today():
                        is_worker = True
                else:
                    is_worker = True
            if self.contract_ids and is_worker \
                    and self.leaves_configuration_id:
                if self.contract_ids[0].trial_date_start:
                    date_start = self.contract_ids[0].trial_date_start
                else:
                    date_start = self.contract_ids[0].date_start
                date_start = datetime.strptime(
                    date_start.replace('-', ''), "%Y%m%d").date()

                date_end = self.contract_ids[-1].date_end
                if date_end and not is_worker:
                    date_end = datetime.strptime(
                        date_end.replace('-', ''), "%Y%m%d").date()
                else:
                    date_end = date.today()

                work_year = date_end.year - date_start.year

                work_month = date_end.month - date_start.month

                if work_month < 0:
                    work_month += 12
                    if work_year:
                        work_year -= 1

                work_days = (date_end.day - date_start.day)

                d = calendar.monthrange(date.today().year, date_end.month)
                if work_days < 0:
                    work_days += d[1]
                    work_month -= 1

                if work_month < 0:
                    work_month += 12
                    if work_year:
                        work_year -= 1
                self.employee_work_days = work_days
                self.employee_work_months = work_month
                self.employee_work_years = work_year

                if work_year >= 1 or (
                            work_month >=
                            self.leaves_configuration_id.minimum_month_work):
                    vacation_days = self.leaves_configuration_id.vacation
                else:
                    vacation_days = (
                        self.leaves_configuration_id.vac_day_per_month
                        * work_month)
                sick_days = self.leaves_configuration_id.sick_leave
                day_off = self.leaves_configuration_id.day_off

                holiday_status = [s.id for s in
                                  self.env['hr.holidays.status'].search(
                                      [('leave_type', 'in', ['vacation',
                                                             'day_off',
                                                             'sick_days'])])]

                holidays = self.env['hr.holidays'].search(
                    [('employee_id', '=', self.id),
                     ('holiday_status_id', 'in', holiday_status),
                     ('state', '=', 'validate')])
                if work_year > 0:
                    start_year = date_start + timedelta(days=365) * work_year
                else:
                    start_year = date_start
                all_leaves = 0
                all_day_off = 0
                all_sick = 0
                for holiday in holidays:
                    if holiday.date_from:
                        date_from = datetime.strptime(
                            holiday.date_from.split(' ')[0].replace('-', ''),
                            "%Y%m%d").date()
                        if date_from > start_year:
                            if (holiday.holiday_status_id.leave_type
                                    == 'vacation'):
                                all_leaves += holiday.number_of_days_temp
                            elif (holiday.holiday_status_id.leave_type
                                      == 'day_off'):
                                all_day_off += holiday.number_of_days_temp
                            elif (holiday.holiday_status_id.leave_type
                                      == 'sick_days'):
                                all_sick += holiday.number_of_days_temp
                credit_leaves_count = \
                    (self.leaves_configuration_id.vac_day_per_month
                     * work_month) - all_leaves
                # if credit_leaves_count > 0:
                #     credit_leaves_count = 0

                leaves_count = vacation_days - all_leaves
                sick_leaves = sick_days - all_sick
                val = {'employee_work_days': int(work_days),
                       'employee_work_months': int(work_month),
                       'employee_work_years': int(work_year),
                       'leaves_count': all_leaves,
                       'credit_leaves_count': credit_leaves_count,
                       'leaves_count_left': leaves_count,
                       'leaves_count_used': credit_leaves_count,
                       'sick_leaves': sick_leaves,
                       'sick_leaves_used': all_sick,
                       'day_off_leaves': all_day_off}

                self.write(val)

                self.leaves_count = all_leaves
                self.leaves_count_left = leaves_count
                self.leaves_count_used = credit_leaves_count
                self.credit_leaves_count = credit_leaves_count
                self.day_off_leaves = all_day_off
                self.sick_leaves = sick_leaves
                self.sick_leaves_used = all_sick
                self.save_leaves_count = 0
                self.env['holiday.history'].create_history(self, start_year)
                if self.holiday_history_ids \
                        and self.leaves_configuration_id.save_vacation:
                    save_leaves_count = self.holiday_history_ids[-1].save_leaves
                    credit_leaves_count += save_leaves_count
                    if credit_leaves_count > 0:
                        credit_leaves_count = 0
                    leaves_count += save_leaves_count
                    self.write({'save_leaves_count': save_leaves_count,
                                'credit_leaves_count': credit_leaves_count,
                                'leaves_count': leaves_count})
                    self.save_leaves_count = save_leaves_count
                    self.credit_leaves_count = credit_leaves_count
                    self.leaves_count = leaves_count

    @api.multi
    def _leaves_count(self):
        res = {}
        for employee in self:

            leaves = self.env['hr.holidays'].read_group(
                [('employee_id', 'in', [employee.id]),
                 ('holiday_status_id.limit', '=', False),
                 ('state', '=', 'validate')],
                fields=['number_of_days',
                        'employee_id'],
                groupby=['employee_id'])
            res.update(dict(
                [(leave['employee_id'][0], leave['number_of_days']) for leave in
                 leaves]))
            employee.leaves_count = res.get(employee.id)
            employee._get_employee_time_work()

    employee_time_work = fields.Float(compute='_get_employee_time_work',
                                      string='Employee Time Work')
    employee_work_days = fields.Integer(string="Employee Work Days")
    employee_work_months = fields.Integer(string="Months Employed This Year")
    employee_work_years = fields.Integer(string="Years Employed")

    leaves_configuration_id = fields.Many2one('hr.holidays.configuration',
                                              string="Leaves Configuration",
                                              required=True)

    leaves_count = fields.Float(compute="_leaves_count",
                                string=' Vacation days taken this year')

    leaves_count_left = fields.Float(compute="_leaves_count",
                                     string='Vacations days left this year')

    leaves_count_used = fields.Float(compute="_leaves_count",
                                     string='Vacation days currently left')

    credit_leaves_count = fields.Float(compute="_leaves_count",
                                       string='Credit Leaves')

    save_leaves_count = fields.Float(compute="_leaves_count",
                                     string='Save Leaves')

    day_off_leaves = fields.Integer(compute="_leaves_count",
                                    string='Day Offs Taken This Year')

    sick_leaves = fields.Integer(compute="_leaves_count",
                                 string='Sick Leaves Left')
    sick_leaves_used = fields.Integer(compute="_leaves_count",
                                      string='Sick Leaves Used')

    holiday_history_ids = fields.One2many('holiday.history',
                                          'employee_id',
                                          string='Holiday History')
    show_in_project_employee = fields.Boolean(string="Show")

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        if self.env.context.get('project'):
            team_bytebrand_project = self.env['bytebrand.project'].search(
                [('team_lead_id', '=', self.env.user)])
            tech_bytebrand_project = self.env['bytebrand.project'].search(
                [('tech_lead_id', '=', self.env.user)])
            bytebrand_projects = (team_bytebrand_project or []) + (
                tech_bytebrand_project or [])
            employees = []
            for bytebrand_project in bytebrand_projects:
                for employee in bytebrand_project.employee_ids:
                    employees.append(employee)
            all_employyes = self.env['hr.employee'].search([])
            for eml in all_employyes:
                if eml in employees:
                    eml.write({'show_in_project_employee': True})
                else:
                    eml.write({'show_in_project_employee': False})
        values = super(HrEmployee, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)
        return values
