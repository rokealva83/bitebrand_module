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
import re
from datetime import date, datetime
import logging

_logger = logging.getLogger(__name__)


def calculate_wage(obj, employees, today_year):
    user_wage = all_wage = 0
    employee_all_work_days = 0
    len_employees = len(employees)
    work_day = 0
    for empl in employees:
        all_work_days = 0
        if empl.contract_ids:
            employee_wage = 0
            contract = empl.contract_ids[0]
            if contract.date_start:
                date_start = contract.date_start
                date_start = datetime.strptime(
                    date_start.replace('-', ''), "%Y%m%d").date()
                date_end = date.today()
                contract_days = (date_end - date_start).days
                all_work_days += contract_days
                if empl == obj:
                    employee_all_work_days = all_work_days
                    day_of_year = (date_end - datetime.strptime(
                        ('%s-01-01' % today_year).replace('-', ''),
                        "%Y%m%d").date()).days

                    if all_work_days > day_of_year:
                        date_start = datetime.strptime(
                            ('%s-01-01' % today_year).replace('-', ''),
                            "%Y%m%d").date()
                        work_day = (date_end - date_start).days
                    else:
                        work_day = all_work_days
                contract_month = (date_end.month - date_start.month)
                if contract_month < 0:
                    contract_month += 12
                contract_year = date_end.year - date_start.year
                if contract_year > 0:
                    contract_month += (12 * contract_year)

                employee_wage = empl.contract_ids[-1].wage
            if not all_work_days:
                len_employees -= 1

            if empl == obj:
                user_wage = employee_wage

            all_wage += employee_wage
    res = {'user_wage': user_wage,
           'all_wage': all_wage,
           'work_days': work_day,
           'all_work_days': employee_all_work_days,
           'len_employees': len_employees}
    # _logger.info('\n res  \n  %s  \n', res)

    return res


class BonusSystemSettings(models.Model):
    _name = 'bonus.system.settings'
    _rec_name = 'year'

    @api.one
    def _get_percentage(self):
        self.percentage = '%s/%s' % (self.fix_bonus, self.calculate_bonus)

    company_id = fields.Many2one('res.company',
                                 string='Company')
    profit = fields.Integer(string='Profit',
                            required=True)
    profit_percentage = fields.Integer(string='Brutto profit, %',
                                       default=100,
                                       required=True)
    fix_bonus = fields.Integer(string='Fix bonus, %',
                               required=True)
    calculate_bonus = fields.Integer(string='Calculate bonus, %')
    percentage = fields.Char(compute='_get_percentage',
                             string='Percentage')
    use_account_balance = fields.Boolean(string="Use Account Balance")
    year = fields.Char(string='Year',
                       required=True)
    account_journal_name = fields.Char(string='Account Journal Name')
    minimum_period = fields.Integer(string='Minimum Month Work',
                                    default=1)
    category_ids = fields.Many2many('hr.employee.category',
                                    'bonus_system_settings_category_rel',
                                    'bonus_system_settings_id',
                                    'category_id',
                                    string='Tags')
    check_system = fields.Boolean(string='Company vs. Tags',
                                  default=True)

    employee_bonus_result_ids = fields.One2many('employee.bonus.result',
                                                'bonus_system_settings_id',
                                                string="Employee Bonus Result")
    archive = fields.Boolean(string="Archive")

    @api.onchange('fix_bonus')
    def _onchange_fix_bonus(self):
        if self.fix_bonus:
            self.calculate_bonus = 100 - self.fix_bonus

    @api.onchange('check_system')
    def _onchange_check_system(self):
        self.company_id = ''
        self.category_ids = ''

    @api.onchange('calculate_bonus')
    def _onchange_calculate_bonus(self):
        if self.calculate_bonus:
            self.fix_bonus = 100 - self.calculate_bonus

    @api.onchange('year')
    def _onchange_year(self):
        year_now = int(date.today().year)
        if self.year:
            if re.findall(r'[\D]', self.year):
                raise ValidationError(
                    _('Invalid symbol'))
            if int(self.year) < year_now or len(self.year) > 4:
                raise ValidationError(
                    _('You can not set this year'))
            bonus = self.search([('company_id', '=', self.company_id.id),
                                 ('year', '=', self.year)])
            if bonus and bonus != self:
                raise ValidationError(
                    _('You can not add dublicate year'))

    @api.model
    def create(self, values):
        year_now = int(date.today().year)
        if int(values.get('year')):
            if re.findall(r'[\D]', values.get('year')):
                raise ValidationError(
                    _('Invalid symbol'))
            if int(values.get('year')) < year_now:
                raise ValidationError(
                    _('You can not set this year'))
            bonus = self.search([('company_id', '=', values.get('company_id')),
                                 ('year', '=', values.get('year'))])
            if bonus:
                raise ValidationError(
                    _('You can not add dublicate year'))
        return super(BonusSystemSettings, self).create(values)

    @api.multi
    def write(self, values):
        if values.get('year'):
            year_now = int(date.today().year)
            if int(values.get('year')):
                if re.findall(r'[\D]', values.get('year')):
                    raise ValidationError(
                        _('Invalid symbol'))
                if int(values.get('year')) < year_now or len(self.year) > 4:
                    raise ValidationError(
                        _('You can not set this year'))
                bonus = self.search(
                    [('company_id', '=', values.get('company_id')),
                     ('year', '=', values.get('year'))])
                if bonus:
                    raise ValidationError(
                        _('You can not add dublicate year'))
        return super(BonusSystemSettings, self).write(values)

    @api.model
    def _scheduler_calculate_bonus(self):
        today_year = date.today().year
        bonus_pool = self.env['bonus.system.settings']
        employee_pool = self.env['hr.employee']
        bonus_settings = bonus_pool.search([('year', '=', today_year)])
        wages = {}
        account_journal_pool = self.env['account.journal']

        employee = employee_pool.search([])
        for e in employee:
            final_calculate_bonus = 0
            calculate_bonus = 0
            shared_profit = 0
            final_fixed_bonus = 0
            fixed_bonus = 0
            for bonus_setting in bonus_settings:
                profit = bonus_setting.profit * bonus_setting.profit_percentage
                if bonus_setting.use_account_balance:
                    account_journal = account_journal_pool.search(
                        [('name', '=', bonus_setting.account_journal_name)])
                    account_balance = 0
                    if account_journal:
                        account_balance = (
                            account_journal.get_journal_dashboard_datas().get(
                                'account_balance'))
                    if account_balance:
                        try:
                            account_balance = float(
                                account_balance.split(' ')[0].replace("'", ""))
                        except:
                            pass

                    profit = ((account_balance + bonus_setting.profit)
                              * bonus_setting.profit_percentage / 100)
                fixed_bonus = 0
                if bonus_setting.check_system and \
                                e.company_id == bonus_setting.company_id:
                    employees = employee_pool.search(
                        [('company_id', '=', bonus_setting.company_id.id)])
                    shared_profit += profit

                    wages = calculate_wage(e, employees, today_year)
                    fixed_bonus += (
                        profit * bonus_setting.fix_bonus / (
                            100 * wages.get('len_employees')))

                    try:
                        profit *= bonus_setting.fix_bonus / 100.0
                        wage_koef = (
                            wages.get('user_wage') /
                            wages.get('all_wage'))
                        calculate_bonus = profit * wage_koef
                    except:
                        pass
                else:
                    calculate = False
                    for category_id in e.category_ids:
                        if category_id in bonus_setting.category_ids \
                                and not calculate:
                            all_employees = employee_pool.search([])
                            employees = []
                            for empl in all_employees:
                                for cat_id in empl.category_ids:
                                    if cat_id in bonus_setting.category_ids \
                                            and empl not in employees:
                                        employees.append(empl)

                            wages = calculate_wage(e, employees, today_year)
                            fixed_bonus += (
                                profit * bonus_setting.fix_bonus / (
                                    100 * wages.get('len_employees')))
                            shared_profit += profit
                            try:
                                profit *= bonus_setting.fix_bonus / 100.0
                                wage_koef = (
                                    wages.get('user_wage') /
                                    wages.get('all_wage'))
                                calculate_bonus = profit * wage_koef
                            except:
                                pass
                            calculate = True
                final_fixed_bonus += fixed_bonus
                final_calculate_bonus += calculate_bonus
            if wages:
                final_fixed_bonus = (
                    final_fixed_bonus * wages.get('work_days') / 365)
                final_calculate_bonus = final_calculate_bonus * wages.get(
                    'work_days') / 365
                final_employee_bonus = final_fixed_bonus + final_calculate_bonus
            else:
                final_employee_bonus = 0
            other_bonus = 0
            for bonus in e.employee_bonus_ids:
                other_bonus += bonus.bonus
            if not wages.get('all_work_days'):
                fixed_bonus = 0
            val = {
                'fixed_bonus': fixed_bonus,
                'final_fixed_bonus': final_fixed_bonus,
                'other_bonus': round(other_bonus, 2),
                'calculate_bonus': calculate_bonus,
                'final_calculate_bonus': final_calculate_bonus,
                'total_bonus': round(final_employee_bonus, 2),
                'shared_profit': shared_profit,
                'user_wage': wages.get('user_wage'),
                'all_wage': wages.get('all_wage'),
                'work_days': wages.get('work_days'),
                'all_work_days': wages.get('all_work_days')
            }
            e.write(val)


class EmployeeBonus(models.Model):
    _name = 'employee.bonus'

    employee_id = fields.Many2one('hr.employee',
                                  string='Employee')
    bonus = fields.Integer(string='Bonus')
    description = fields.Char(string='Description')


class EmployeeBonusResult(models.Model):
    _name = "employee.bonus.result"

    bonus_system_settings_id = fields.Many2one('bonus.system.settings',
                                               string='Employee')
    employee_id = fields.Many2one('hr.employee',
                                  string='Employee')
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
