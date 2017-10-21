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
from datetime import date, datetime
import calendar
import logging

_logger = logging.getLogger(__name__)


class EmployeeSalarySystem(models.Model):
    _name = 'employee.salary.system'
    _rec_name = 'period'

    @api.model
    def default_get(self, fields):
        res = super(EmployeeSalarySystem, self).default_get(fields)

        exchange_rate = 25
        fixed_monthly_tax = 704
        account_service = 500
        bank_commission = 9

        salary_employees = []
        employee_pool = self.env['hr.employee']
        employees = employee_pool.search([])

        month = date.today().month
        year = date.today().year
        if month == 1:
            month = 12
            year = year - 1
        else:
            month = month - 1
        day_in_month = calendar.monthrange(year, month)
        day = 1
        work_day = [0, 1, 2, 3, 4]
        work_days = 0
        while day <= day_in_month[1]:
            if calendar.weekday(year, month, day) in work_day:
                work_days += 1
            day += 1

        for employee in employees:
            emp = {'employee_id': employee.id,
                   'exchange_rate': exchange_rate,
                   'fixed_monthly_tax': fixed_monthly_tax,
                   'account_service': account_service,
                   'bank_commission': bank_commission}
            if employee and employee.contract_ids:
                check_contract = self.check_user_contract(
                    employee=employee, period_date=None)
                emp.update(salary=check_contract.get('contract_salary'),
                           contract_id=check_contract.get('contract_id'))
            else:
                emp.update(salary=0.00)
            day_off_num = self.check_day_off(employee, None)
            emp.update(day_off=day_off_num)

            employee_salary = self.env['employee.salary'].create(emp)
            salary_employees.append(employee_salary.id)
        res.update(employee_salary_ids=salary_employees,
                   exchange_rate=exchange_rate,
                   fixed_monthly_tax=fixed_monthly_tax,
                   account_service=account_service,
                   bank_commission=bank_commission,
                   work_day_in_month=work_days,
                   )
        return res

    employee_salary_ids = fields.One2many(
        'employee.salary',
        'employee_salary_system_id',
        string='Employee Salary',
        readonly=True,
        states={'draft': [('readonly', False)]})
    date = fields.Date(string='Date',
                       required=True,
                       readonly=True,
                       states={'draft': [('readonly', False)]})
    period = fields.Char(string='Period',
                         required=True,
                         readonly=True,
                         states={'draft': [('readonly', False)]})
    exchange_rate = fields.Float(string='Exchange Rate, UAH/USD',
                                 required=True,
                                 readonly=True,
                                 states={'draft': [('readonly', False)]})
    fixed_monthly_tax = fields.Float(string='Fixed Monthly Tax, UAH',
                                     readonly=True,
                                     states={'draft': [('readonly', False)]})
    bank_commission = fields.Float(string='Bank Commission, UAH',
                                   readonly=True,
                                   states={'draft': [('readonly', False)]})
    account_service = fields.Float(string='Account Service, UAH',
                                   readonly=True,
                                   states={'draft': [('readonly', False)]})
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm'),
                                        ('bills', 'Bills'),
                                        ('paid', 'Paid')],
                             string='State',
                             default='draft',
                             readonly=True,
                             states={'draft': [('readonly', False)]})
    work_day_in_month = fields.Integer(string='Work Days In Month')

    @api.multi
    def check_day_off(self, employee, period_date=None):
        if not period_date:
            period_date = date.today()
            month = period_date.month
            year = period_date.year
            if month == 1:
                month = 12
                year = year - 1
            else:
                month = month - 1
        else:
            month = period_date.month
            year = period_date.year
        day_in_month = calendar.monthrange(year, month)
        day = 1
        work_day = [0, 1, 2, 3, 4]
        work_days = 0
        while day <= day_in_month[1]:
            if calendar.weekday(year, month, day) in work_day:
                work_days += 1
            day += 1

        start_period = datetime.strptime(
            '%s%s01' % (year, month), "%Y%m%d").date()
        end_period = datetime.strptime(
            '%s%s%s' % (year, month, day_in_month[1]), "%Y%m%d").date()

        holidays_status = self.env['hr.holidays.status'].search(
            [('leave_type', '=', 'day_off')])
        hr_holidays = self.env['hr.holidays'].search(
            [('employee_id', '=', employee.id),
             ('holiday_status_id', '=', holidays_status[0].id),
             ('state', '=', 'validate')])
        day_off_num = 0
        check_holidays = []
        for holiday in hr_holidays:
            date_from = datetime.strptime(
                holiday.date_from.split(' ')[0].replace('-', ''),
                "%Y%m%d").date()
            if start_period <= date_from <= end_period:
                if holiday.number_of_days_temp > 1:
                    date_to = datetime.strptime(
                        holiday.date_to.split(' ')[0].replace('-', ''),
                        "%Y%m%d").date()
                    if date_to.month != month:
                        day_off_num = day_in_month[1] - date_from.day + 1
                    else:
                        day_off_num += holiday.number_of_days_temp
                else:
                    day_off_num += holiday.number_of_days_temp
                check_holidays.append(holiday)
        for holiday in hr_holidays:
            date_to = datetime.strptime(
                holiday.date_to.split(' ')[0].replace('-', ''),
                "%Y%m%d").date()
            if start_period <= date_to <= end_period \
                    and holiday not in check_holidays:
                day_off_num += date_to.day
        return day_off_num

    @api.onchange('exchange_rate')
    def onchange_exchange_rate(self):
        for line in self.employee_salary_ids:
            line.exchange_rate = self.exchange_rate
        self.calculate()

    @api.onchange('fixed_monthly_tax')
    def onchange_fixed_monthly_tax(self):
        for line in self.employee_salary_ids:
            line.fixed_monthly_tax = self.fixed_monthly_tax
        self.calculate()

    @api.onchange('bank_commission')
    def onchange_bank_commission(self):
        for line in self.employee_salary_ids:
            line.bank_commission = self.bank_commission
        self.calculate()

    @api.onchange('account_service')
    def onchange_account_service(self):
        for line in self.employee_salary_ids:
            line.account_service = self.account_service
        self.calculate()

    @api.multi
    def check_user_day_off(self, employee, period_date=None):
        user_day_off = {}
        year, month, day_in_month, start_period, end_period = \
            self.check_period(period_date)
        day = 1
        work_day = [0, 1, 2, 3, 4]
        work_days = 0
        while day <= day_in_month[1]:
            if calendar.weekday(year, month, day) in work_day:
                work_days += 1
            day += 1

        holidays_status = self.env['hr.holidays.status'].search(
            [('leave_type', '=', 'day_off')])
        hr_holidays_pool = self.env['hr.holidays']

        hr_holidays = hr_holidays_pool.search(
            [('employee_id', '=', employee.id),
             ('holiday_status_id', '=', holidays_status[0].id),
             ('state', 'in', ('validate', 'confirm'))])
        day_off_num = 0
        day_off_dict = []
        for holiday in hr_holidays:
            need_holiday = False
            holiday_date_start = datetime.strptime(
                holiday.date_from.split(' ')[0].replace('-', ''),
                "%Y%m%d").date()
            holiday_date_finish = datetime.strptime(
                holiday.date_to.split(' ')[0].replace('-', ''),
                "%Y%m%d").date()
            number_of_days = holiday.number_of_days_temp

            if start_period <= holiday_date_start <= end_period \
                    or start_period <= holiday_date_finish <= end_period:
                need_holiday = True
            if need_holiday:
                if number_of_days == 1:
                    day_off_dict.append(holiday_date_start.day)
                    day_off_num += 1
                else:
                    if holiday_date_start.month == holiday_date_finish.month:
                        day_off_num += number_of_days
                        day = holiday_date_start.day
                        while day <= holiday_date_finish.day:
                            day_off_dict.append(day)
                            day += 1
                    elif holiday_date_start.month == start_period.month:
                        day = holiday_date_start.day
                        while day <= end_period.day:
                            day_off_dict.append(day)
                            day_off_num += 1
                            day += 1
                    elif holiday_date_finish.month == start_period.month:
                        day = start_period.day
                        while day <= holiday_date_finish.day:
                            day_off_dict.append(int(day))
                            day_off_num += 1
                            day += 1

                user_day_off['day_off_dict'] = day_off_dict
        user_day_off['day_off_num'] = day_off_num

        holidays_status = self.env['hr.holidays.status'].search(
            [('leave_type', '=', 'vacation')])
        hr_holidays_pool = self.env['hr.holidays']

        hr_holidays = hr_holidays_pool.search(
            [('employee_id', '=', employee.id),
             ('holiday_status_id', '=', holidays_status[0].id),
             ('state', 'in', ('validate', 'confirm')),
             ('date_from', '!=', None)])
        vacation_num = 0
        for holiday in hr_holidays:
            need_holiday = False
            holiday_date_start = datetime.strptime(
                holiday.date_from.split(' ')[0].replace('-', ''),
                "%Y%m%d").date()
            holiday_date_finish = datetime.strptime(
                holiday.date_to.split(' ')[0].replace('-', ''),
                "%Y%m%d").date()
            number_of_days = holiday.number_of_days_temp

            if start_period <= holiday_date_start <= end_period \
                    or start_period <= holiday_date_finish <= end_period:
                need_holiday = True
            if need_holiday:
                if number_of_days == 1:
                    vacation_num += 1
                else:
                    if holiday_date_start.month == holiday_date_finish.month:
                        vacation_num += number_of_days
                        day = holiday_date_start.day
                        while day <= holiday_date_finish.day:
                            day += 1

                    elif holiday_date_start.month == start_period.month:
                        day = holiday_date_start.day
                        while day <= end_period.day:
                            vacation_num += 1
                            day += 1

                    elif holiday_date_finish.month == start_period.month:
                        day = start_period.day
                        while day <= holiday_date_finish.day:
                            vacation_num += 1
                            day += 1
        user_day_off['vacation_num'] = vacation_num

        holidays_status = self.env['hr.holidays.status'].search(
            [('leave_type', '=', 'sick_days')])
        hr_holidays_pool = self.env['hr.holidays']

        hr_holidays = hr_holidays_pool.search(
            [('employee_id', '=', employee.id),
             ('holiday_status_id', '=', holidays_status[0].id),
             ('state', 'in', ('validate', 'confirm')),
             ('date_from', '!=', None)])
        sick_num = 0
        for holiday in hr_holidays:
            need_holiday = False
            holiday_date_start = datetime.strptime(
                holiday.date_from.split(' ')[0].replace('-', ''),
                "%Y%m%d").date()
            holiday_date_finish = datetime.strptime(
                holiday.date_to.split(' ')[0].replace('-', ''),
                "%Y%m%d").date()
            number_of_days = holiday.number_of_days_temp

            if start_period <= holiday_date_start <= end_period \
                    or start_period <= holiday_date_finish <= end_period:
                need_holiday = True
            if need_holiday:
                if number_of_days == 1:
                    sick_num += 1
                else:
                    if holiday_date_start.month == holiday_date_finish.month:
                        sick_num += number_of_days
                        day = holiday_date_start.day
                        while day <= holiday_date_finish.day:
                            day += 1

                    elif holiday_date_start.month == start_period.month:
                        day = holiday_date_start.day
                        while day <= end_period.day:
                            sick_num += 1
                            day += 1

                    elif holiday_date_finish.month == start_period.month:
                        day = start_period.day
                        while day <= holiday_date_finish.day:
                            sick_num += 1
                            day += 1

        user_day_off['sick_num'] = sick_num

        return user_day_off

    def check_work_day(self, start_day, month, year, end_day,
                       holidays_in_period=None):
        day = start_day
        work_day = [0, 1, 2, 3, 4]
        work_days_num = 0
        while day <= end_day:
            if calendar.weekday(year, month, day) in work_day:
                if int(day) not in holidays_in_period:
                    work_days_num += 1
            day += 1
        return work_days_num

    def check_contract_work_day(self, start_day, month, year, end_day,
                                holidays_in_period=None, user_day_off=None):
        day = start_day
        work_day = [0, 1, 2, 3, 4]
        contract_work_days = 0
        need_work_days = 0
        real_work_day = 0
        contract_work_days_dict = []
        day_off_dict = user_day_off.get('day_off_dict')
        while day <= end_day:
            if calendar.weekday(year, month, day) in work_day:
                contract_work_days += 1
                contract_work_days_dict.append(day)
                if int(day) not in holidays_in_period:
                    need_work_days += 1
                    if not day_off_dict:
                        day_off_dict = []
                    if int(day) not in day_off_dict:
                        real_work_day += 1
            day += 1
        return contract_work_days, contract_work_days_dict, need_work_days, real_work_day

    def check_period(self, period_date):
        if not period_date:
            period_date = date.today()
            month = period_date.month
            year = period_date.year
            if month == 1:
                month = 12
                year -= 1
            else:
                month -= 1
        else:
            month = period_date.month
            year = period_date.year

        day_in_month = calendar.monthrange(year, month)
        start_period = datetime.strptime(
            '%s%s01' % (year, month), "%Y%m%d").date()
        end_period = datetime.strptime(
            '%s%s%s' % (year, month, day_in_month[1]), "%Y%m%d").date()
        return year, month, day_in_month, start_period, end_period

    @api.multi
    def check_holidays_in_period(self, year, start_period, end_period):
        hr_holidays_public = self.env['hr.holidays.public'].search(
            [('year', '=', year)])
        holidays_in_period = []
        if not hr_holidays_public:
            raise ValidationError(
                _('You have not Public Holidays Info'))
        else:
            if hr_holidays_public.line_ids:
                for line in hr_holidays_public.line_ids:
                    holiday_date = datetime.strptime(
                        line.date.replace('-', ''),
                        "%Y%m%d").date()
                    if start_period <= holiday_date <= end_period:
                        holidays_in_period.append(int(holiday_date.day))
        return holidays_in_period

    @api.multi
    def check_user_contract(self, employee, period_date=None):
        user_day_off = self.check_user_day_off(employee, period_date)
        year, month, day_in_month, start_period, end_period = \
            self.check_period(period_date)

        salary = 0.00
        holidays_in_period = self.check_holidays_in_period(
            year, start_period, end_period)
        contract_id = None
        rate = False
        wage = 0
        if employee.contract_ids:
            for contract in employee.contract_ids:

                contract_date_start = datetime.strptime(
                    contract.date_start.replace('-', ''), "%Y%m%d").date()
                if contract.date_end:
                    contract_date_end = datetime.strptime(
                        contract.date_end.replace('-', ''), "%Y%m%d").date()
                else:
                    contract_date_end = end_period
                calculate_contract = False
                if (contract_date_start <= start_period) \
                        and (contract_date_end >= end_period
                             or (start_period <=
                                     contract_date_end <= end_period)):
                    calculate_contract = True
                elif start_period <= contract_date_start <= end_period:
                    calculate_contract = True

                if calculate_contract:
                    contract_id = contract.id
                    if not contract.rate:
                        if contract_date_start < start_period:
                            start_day = 1
                        else:
                            start_day = contract_date_start.day
                        if end_period <= contract_date_end:
                            end_day = day_in_month[1]
                        else:
                            end_day = contract_date_end.day

                        (contract_work_days, contract_work_days_dict,
                         need_work_days,
                         real_work_day) = self.check_contract_work_day(
                            start_day, month, year, end_day, holidays_in_period,
                            user_day_off)
                        work_day_in_month = self.check_work_day(
                            start_period.day, month, year, end_period.day,
                            holidays_in_period)
                        contract_wage = (contract.wage / work_day_in_month
                                         * need_work_days)
                        wage += contract_wage

                        contract_salary = contract_wage / need_work_days * (
                            need_work_days - (need_work_days - real_work_day))
                        salary += contract_salary
                    else:
                        rate = True

        result = {'contract_id': contract_id,
                  'contract_salary': wage, 'salary': salary,
                  'day_off': user_day_off.get('day_off_num'),
                  'vacation': user_day_off.get('vacation_num'),
                  'sick': user_day_off.get('sick_num'),
                  'holidays_in_period': holidays_in_period, 'rate': rate, }

        return result

    @api.multi
    def calculate(self, lines=None):
        if not lines:
            lines = self.employee_salary_ids
        if self.date:
            period_date = datetime.strptime(self.date.replace('-', ''),
                                            "%Y%m%d").date()
        else:
            period_date = None
        year, month, day_in_month, start_period, end_period = \
            self.check_period(period_date)
        holidays_in_period = self.check_holidays_in_period(year, start_period,
                                                           end_period)
        self.work_day_in_month = self.check_work_day(
            start_period.day, month, year, end_period.day, holidays_in_period)

        for line in lines:

            result = self.check_user_contract(line.employee_id, period_date)
            day_off = result.get('day_off')
            vacation = result.get('vacation')
            sick = result.get('sick')
            line.contract_id = result.get('contract_id')

            line.day_off = day_off
            if not result.get('rate'):
                salary = result.get('contract_salary')
                total_salary = result.get('salary') + line.bonus
            else:
                salary = line.salary
                total_salary = salary + line.bonus

            total_expenses = (line.account_software_keys + line.other_expenses +
                              line.fixed_monthly_tax + line.account_service +
                              line.bank_commission)
            total_expenses_currency = total_expenses / line.exchange_rate
            salary_and_expenses_currency = (
                total_expenses_currency + total_salary)
            salary_and_expenses = (
                salary_and_expenses_currency * line.exchange_rate)
            total_tax = 0.00
            if not line.employee_id.tax_free:
                total_tax = salary_and_expenses * 0.05 * (
                    1 + 0.05 * (1 + 0.05 * (1 + 0.05)))
            total = total_tax + salary_and_expenses
            total_currency = total / line.exchange_rate

            line.total_salary = total_salary
            line.total_expenses = total_expenses
            line.total_expenses_currency = total_expenses_currency
            line.salary_and_expenses_currency = salary_and_expenses_currency

            line.salary_and_expenses = salary_and_expenses

            line.total_tax = total_tax
            line.total = total
            line.total_currency = total_currency

            effective_hours = (self.work_day_in_month * 8 - line.day_off * 8
                               - sick * 8 - vacation * 8)
            line.effective_hours = effective_hours

            line.write({'salary': salary,
                        'total_salary': total_salary,
                        'day_off': day_off,
                        'effective_hours': effective_hours,
                        'total_expenses': total_expenses,
                        'total_expenses_currency': total_expenses_currency,
                        'salary_and_expenses_currency':
                            salary_and_expenses_currency,
                        'salary_and_expenses': salary_and_expenses,
                        'total_tax': total_tax,
                        'total': total,
                        'total_currency': total_currency})

    @api.multi
    def recalculate(self):
        self.calculate()

    @api.model
    def create(self, values):
        res = super(EmployeeSalarySystem, self).create(values)
        if values.get('employee_salary_ids'):
            ids = [i[1] for i in values.get('employee_salary_ids')]
            self.env['employee.salary'].browse(ids).write(
                {'employee_salary_system_id': res.id})
        salary = self.env['employee.salary'].search(
            [('employee_salary_system_id', '=', None)])
        if salary:
            salary.unlink()
        return res

    @api.multi
    def action_confirm(self):
        self.write({'state': 'confirm'})

    @api.multi
    def action_done(self):
        self.write({'state': 'done'})

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def create_vendor_bills(self):
        res_partner_pool = self.env['res.partner']

        account_invoice_pool = self.env['account.invoice']

        account_invoice_line_pool = self.env['account.invoice.line']

        res_currency_pool = self.env['res.currency']
        res_currency = res_currency_pool.search([('name', '=', 'USD')])

        account_journal_pool = self.env['account.journal']
        journal = account_journal_pool.search(
            [('type', '=', 'purchase'),
             ('currency_id', '=', res_currency.id)])
        for employee_salary_line in self.employee_salary_ids:
            vendor = res_partner_pool.search(
                [('supplier', '=', True),
                 ('employee_id', '=', employee_salary_line.employee_id.id)])
            if not vendor:
                raise ValidationError(
                    _('Employee %s has no partner'
                      % employee_salary_line.employee_id.name))
            if not vendor.product_default_id:
                raise ValidationError(
                    _('Vendor %s has no default product' % vendor.name))
            invoice_values = {'partner_id': vendor.id,
                              'currency_id': res_currency.id,
                              'journal_id': journal.id,
                              'account_id':
                                  vendor.property_account_payable_id.id,
                              'type': 'in_invoice',
                              'payment_term_id':
                                  vendor.property_supplier_payment_term_id.id,
                              'date_invoice': datetime.strptime(
                                  self.date.replace('-', ''), "%Y%m%d").date(),
                              'date_due': datetime.strptime(
                                  self.date.replace('-', ''), "%Y%m%d").date()}

            invoice = account_invoice_pool.create(invoice_values)
            line_values = {
                'invoice_id': invoice.id,
                'product_id': vendor.product_default_id.id,
                'name': vendor.product_default_id.name,
                'account_id':
                    vendor.product_default_id.property_account_expense_id.id,
                'quantity': 1,
                'price_unit': employee_salary_line.total_currency
            }
            account_invoice_line_pool.create(line_values)
        self.write({'state': 'bills'})


class EmployeeSalary(models.Model):
    _name = 'employee.salary'

    employee_id = fields.Many2one('hr.employee',
                                  string='Employee')
    employee_salary_system_id = fields.Many2one('employee.salary.system',
                                                string='Employee Salary System')
    contract_id = fields.Many2one('hr.contract', string="Contract")
    day_off = fields.Float(string='Day Off',
                           default=0)
    effective_hours = fields.Integer(string='Effective Hours')
    salary = fields.Float(string="Salary, USD")
    bonus = fields.Float(string='Bonus, USD')
    total_salary = fields.Float(string='Total Salary, USD',
                                store=True)

    other_expenses = fields.Float(string='Other Expenses, UAH')
    account_software_keys = fields.Float(string='Accountant Software Keys, UAH')
    account_service = fields.Float(string='Accountant Service, UAH')
    fixed_monthly_tax = fields.Float(string='Fixed Monthly Tax, UAH')
    bank_commission = fields.Float(string='Bank Commission, UAH')

    total_expenses = fields.Float(string='Total Expenses, UAH')
    total_expenses_currency = fields.Float(string='Total Expenses, USD')
    exchange_rate = fields.Float(string='Exchange Rate, UAH/USD')

    salary_and_expenses = fields.Float(string='Total Salary And Expenses, UAH')
    salary_and_expenses_currency = fields.Float(
        string='Total Salary And Expenses, USD')

    total_tax = fields.Float(string='Total Tax, UAH')

    total = fields.Float(string='Total, UAH')
    total_currency = fields.Float(string='Total, USD')

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if not self.employee_salary_system_id.period \
                or self.employee_salary_system_id.exchange_rate == 0.00 \
                or not self.employee_salary_system_id.date:
            raise ValidationError(
                _('Added Period, Date or Exchange Rate'))

        self.exchange_rate = self.employee_salary_system_id.exchange_rate
        self.fixed_monthly_tax = self.employee_salary_system_id.fixed_monthly_tax
        self.account_service = self.employee_salary_system_id.account_service
        self.bank_commission = self.employee_salary_system_id.bank_commission

        if self.employee_id and self.employee_id.contract_ids:
            date = self.employee_salary_system_id.date
            self.salary = self.employee_id.contract_ids[-1].wage
            self.contract_id = self.employee_id.contract_ids[-1].id

            for contract in self.employee_id.contract_ids:
                if contract.date_end and contract.date_end >= date:
                    self.salary = contract.wage
                    self.contract_id = contract.wage.id
        else:
            self.salary = 0.00
        self.employee_salary_system_id.calculate(lines=self)
