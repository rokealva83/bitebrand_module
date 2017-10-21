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
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta
import logging
from odoo import SUPERUSER_ID

_logger = logging.getLogger(__name__)


class HrHolidaysStatus(models.Model):
    _inherit = "hr.holidays.status"

    @api.multi
    def _user_left_days(self):
        employee_id = None
        if 'employee_id' in self.env.context:
            employee_id = self.env.context['employee_id']
        else:
            employee_ids = self.env['hr.employee'].search(
                [('user_id', '=', self.env.uid)])
            if employee_ids:
                employee_id = employee_ids[0]
        if employee_id:
            employee = self.env['hr.employee'].browse(employee_id)
            for status in self:
                if status.leave_type == 'day_off':
                    status.max_leaves = employee.leaves_configuration_id.day_off
                    status.virtual_remaining_leaves = employee.day_off_leaves
                if status.leave_type == 'sick_days':
                    status.max_leaves = employee.leaves_configuration_id.sick_leave
                    status.virtual_remaining_leaves = employee.sick_leaves
                if status.leave_type == 'vacation':
                    status.max_leaves = employee.leaves_configuration_id.vacation + employee.save_leaves_count
                    status.virtual_remaining_leaves = employee.leaves_count_left

    name = fields.Char(string='Name',
                       required=True,
                       translate=True)
    leave_type = fields.Selection([('day_off', 'Day Off'),
                                   ('sick_days', 'Sick Days'),
                                   ('vacation', 'Vacation'),
                                   ('b-day', 'B-Day'), ],
                                  string='Leave Type',
                                  required=True)
    max_leaves = fields.Integer(compute='_user_left_days',
                                string='Maximum Allowed', )
    virtual_remaining_leaves = fields.Integer(compute="_user_left_days",
                                              string='Virtual Remaining Leaves')

    @api.multi
    def name_get(self):
        if not self.env.context.get('employee_id'):
            return super(HrHolidaysStatus, self).name_get()
        employee = self.env['hr.employee'].browse(
            self.env.context.get('employee_id'))
        res = []
        for record in self:
            name = record.name
            if not employee.leaves_configuration_id.unlimited_day_off:
                if record.leave_type in ['sick_days', 'vacation', 'day_off']:
                    name = '%s %s/%s' % (name,
                                         record.virtual_remaining_leaves,
                                         record.max_leaves)
            else:
                if record.leave_type in ['sick_days', 'vacation']:
                    name = '%s %s/%s' % (name,
                                         record.virtual_remaining_leaves,
                                         record.max_leaves)
            res.append((record.id, name))
        return res


class HrHolidays(models.Model):
    _name = "hr.holidays"
    _inherit = "hr.holidays"

    @api.multi
    def _check_date(self):
        holidays_status = self.env['hr.holidays.status'].search(
            [('leave_type', '=', 'b-day')])
        try:
            holidays_status = holidays_status[0]
        except:
            pass
        for holiday in self:
            if holiday.holiday_status_id.id == holidays_status.id:
                domain = [
                    ('date_from', '<=', holiday.date_to),
                    ('date_to', '>=', holiday.date_from),
                    ('employee_id', '=', holiday.employee_id.id),
                    ('id', '!=', holiday.id),
                    ('state', 'not in', ['cancel', 'refuse']),
                    ('holiday_status_id', '=', holidays_status.id)
                ]
            else:
                domain = [
                    ('date_from', '<=', holiday.date_to),
                    ('date_to', '>=', holiday.date_from),
                    ('employee_id', '=', holiday.employee_id.id),
                    ('id', '!=', holiday.id),
                    ('state', 'not in', ['cancel', 'refuse']),
                    ('holiday_status_id', '!=', holidays_status.id)
                ]
            nholidays = self.search_count(domain)
            if nholidays:
                return False
        return True

    show_in_project_employee = fields.Boolean(string="Show")

    _constraints = [
        (_check_date, 'You can not have 2 leaves that overlaps on same day!',
         ['date_from', 'date_to']),
    ]

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        if self.env.context.get('project'):
            bytebrand_project_pool = self.env['bytebrand.project']
            team_bytebrand_project = bytebrand_project_pool.search(
                [('team_lead_id', '=', self.env.uid)])
            tech_bytebrand_project = bytebrand_project_pool.search(
                [('tech_lead_id', '=', self.env.uid)])
            bytebrand_projects = (team_bytebrand_project or []) + (
                tech_bytebrand_project or [])
            employees = []
            for bytebrand_project in bytebrand_projects:
                for employee in bytebrand_project.employee_ids:
                    employees.append(employee)
            holidays_pool = self.env['hr.holidays']

            all_holidays = holidays_pool.search([])
            view_holidays = []
            not_view_holidays = []
            for holiday in all_holidays:
                if holiday.employee_id in employees:
                    view_holidays.append(holiday.id)
                else:
                    not_view_holidays.append(holiday.id)
            if view_holidays:
                holidays_pool.write(view_holidays,
                                    {'show_in_project_employee': True})
            if not_view_holidays:
                holidays_pool.write(not_view_holidays,
                                    {'show_in_project_employee': False})

        values = super(HrHolidays, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)
        return values

    @api.multi
    def check_holidays(self):
        return True

    @api.model
    def create(self, values):

        self.check_day(values)
        followers = []
        employee_pool = self.env['hr.employee']
        employee = employee_pool.browse(values.get('employee_id'))
        _logger.info(employee)
        group_pool = self.pool.get('res.groups')

        group_id = group_pool.search(
            self.env.cr, SUPERUSER_ID, [('name', '=', 'Approve Vacation')])
        group = group_pool.browse(
            self.env.cr, SUPERUSER_ID, group_id, context=self.env.context)
        for user in group.users:
            if user not in followers:
                followers.append(user)
        projects = self.env['bytebrand.project'].search(
            [('state', '=', 'process')])
        for project in projects:
            if employee in project.employee_ids:
                if project.team_lead_id not in followers:
                    followers.append(project.team_lead_id)
                if project.tech_lead_id not in followers:
                    followers.append(project.tech_lead_id)
        if followers:
            message_follower_ids = values.get('message_follower_ids') or []
            for user in followers:
                if user:
                    message_follower_ids += (
                        self.env['mail.followers']._add_follower_command(
                            self._name, [], {user.partner_id.id: None}, {},
                            force=False)[0])
            values['message_follower_ids'] = message_follower_ids
        return super(HrHolidays, self).create(values)

    @api.multi
    def write(self, values):
        if values.get('number_of_days_temp'):
            self.check_day(
                {'number_of_days_temp': values.get('number_of_days_temp'),
                 'employee_id': self.employee_id.id,
                 'holiday_status_id': self.holiday_status_id.id})
        return super(HrHolidays, self).write(values)

    @api.multi
    def check_day(self, post):
        employee = self.env['hr.employee'].browse(
            post.get('employee_id'))
        leave_type = self.env['hr.holidays.status'].browse(
            post.get('holiday_status_id')).leave_type
        if post.get('number_of_days_temp'):
            if leave_type == 'vacation' \
                    and (int(post.get('number_of_days_temp')) >
                                 employee.leaves_count_left + employee.save_leaves_count):
                raise ValidationError(_("Unfortunately you can't take "
                                        "more than 18 days of paid vacation"))
            elif leave_type == 'day_off':
                day_off = employee.day_off_leaves + int(
                    post.get('number_of_days_temp'))
                if not employee.leaves_configuration_id.unlimited_day_off \
                        and day_off > employee.leaves_configuration_id.day_off:
                    raise ValidationError(_(
                        'Please contact your mentor '
                        'if you need to take more days off'))
            elif leave_type == 'sick_days' \
                    and int(
                        post.get('number_of_days_temp')) > employee.sick_leaves:
                raise ValidationError(_('Please contact your mentor if you '
                                        'need to take more sick leaves'))

    @api.multi
    @api.onchange('holiday_status_id')
    def onchange_holiday_status_id(self, holiday_status_id):
        holidays_status = self.env['hr.holidays.status'].browse(
            holiday_status_id)
        if holidays_status.leave_type == 'b-day' and self.env.uid != 1:
            raise ValidationError(_("You can`t use this Leave type"))

    @api.multi
    def create_holiday_b_date(self, employee, holidays_status):
        day = employee.birthday.split('-')[2]
        mounth = employee.birthday.split('-')[1]
        new_year = date.today().year
        birthday = '%s-%s-%s' % (new_year, mounth, day)
        holiday_values = {
            'name': 'B-DAY',
            'holiday_status_id': holidays_status.id,
            'employee_id': employee.id,
            'date_from': '%s 00:00:00' % birthday,
            'date_to': '%s 20:59:59' % birthday
        }
        b_day = self.create(holiday_values)
        b_day.holidays_validate()
        return True

    @api.model
    def create_b_day(self):
        employees = self.env['hr.employee'].search([])
        holidays_status = self.env['hr.holidays.status'].search(
            [('leave_type', '=', 'b-day')])
        for employee in employees:
            if employee.birthday:
                hr_holidays = self.search(
                    [('holiday_status_id', '=', holidays_status.id),
                     ('employee_id', '=', employee.id)])
                holiday_years = []
                if not hr_holidays:
                    self.create_holiday_b_date(employee, holidays_status)
                for holiday in hr_holidays:
                    holiday_years.append(
                        holiday.date_from.split(' ')[0].split('-')[0])
                    if str(date.today().year) not in holiday_years:
                        self.create_holiday_b_date(employee, holidays_status)
        return True


class HolidayHistory(models.Model):
    _name = "holiday.history"

    year_number = fields.Integer(string="Year Number")
    period = fields.Char(string="Period")
    employee_id = fields.Many2one('hr.employee',
                                  string="Employee")
    leaves_count = fields.Char(string='Number of Leaves')
    day_off_leaves = fields.Char(string='Day Off Leaves')
    sick_leaves = fields.Char(string='Sick Leaves')
    save_leaves = fields.Float(string='Save Leaves')

    @api.multi
    def create_history(self, employee_id, start_date):

        if (len(employee_id.holiday_history_ids) <
                employee_id.employee_work_years):
            i = 0
            holiday_status = [s.id for s in
                              self.env['hr.holidays.status'].search(
                                  [('leave_type', 'in',
                                    ['vacation', 'day_off',
                                     'sick_days', 'day_off_np'])])]
            holidays = self.env['hr.holidays'].search(
                [('employee_id', '=', employee_id.id),
                 ('holiday_status_id', 'in', holiday_status),
                 ('state', '=', 'validate')])
            save_leaves = 0
            while employee_id.employee_work_years > i:
                start_year = start_date.year - (
                    employee_id.employee_work_years - i)
                start_month = start_date.month
                start_day = start_date.day
                d = '%s %s %s' % (start_year, start_month, start_day)
                new_start_date = datetime.strptime(
                    d.replace(' ', ''), "%Y%m%d").date()

                e_d = '%s %s %s' % (start_year + 1, start_month, start_day)
                end_date = datetime.strptime(
                    e_d.replace(' ', ''),
                    "%Y%m%d").date() - timedelta(days=1)
                i += 1

                all_leaves = 0
                all_day_off = 0
                all_sick = 0
                period = '%s - %s' % (new_start_date, end_date)
                for holiday in holidays:
                    if holiday.date_from:
                        date_from = datetime.strptime(
                            holiday.date_from.split(' ')[0].replace('-', ''),
                            "%Y%m%d").date()
                        date_to = datetime.strptime(
                            holiday.date_to.split(' ')[0].replace('-', ''),
                            "%Y%m%d").date()
                        if date_from > new_start_date and date_to <= end_date:
                            if (holiday.holiday_status_id.leave_type
                                    == 'vacation'):
                                all_leaves += holiday.number_of_days_temp
                            elif (holiday.holiday_status_id.leave_type
                                      == 'day_off') or \
                                    (holiday.holiday_status_id.leave_type
                                         == 'day_off_np'):
                                all_day_off += holiday.number_of_days_temp
                            elif (holiday.holiday_status_id.leave_type
                                      == 'sick_days'):
                                all_sick += holiday.number_of_days_temp
                if employee_id.leaves_configuration_id.save_vacation:
                    save_leaves += (
                        employee_id.leaves_configuration_id.vacation -
                        int(all_leaves))
                if save_leaves > 18:
                    save_leaves = 18

                all_leaves = '%s/%s' % (
                    int(all_leaves),
                    employee_id.leaves_configuration_id.vacation)
                all_sick = '%s/%s' % (
                    int(all_sick),
                    employee_id.leaves_configuration_id.sick_leave)
                all_day_off = '%s/%s' % (
                    int(all_day_off),
                    employee_id.leaves_configuration_id.day_off)
                values = {
                    'year_number': i,
                    'period': period,
                    'employee_id': employee_id.id,
                    'leaves_count': all_leaves,
                    'day_off_leaves': all_day_off,
                    'sick_leaves': all_sick,
                    'save_leaves': save_leaves,
                }
                self.create(values)
