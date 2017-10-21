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
import requests
import json
from odoo.exceptions import UserError
from datetime import datetime, date


class JiraWorklog(models.Model):
    _name = 'jira.worklog'

    jira_project_connector_id = fields.Many2one('jira.project.connector',
                                                string='Jira Project')
    email = fields.Char(string='Email')
    time = fields.Char(string='Time')
    task_key = fields.Char(string='Task Key')
    time_log = fields.Char(string='Time Create Log')
    project = fields.Char(string='Project')
    author = fields.Char(string='Author')
    worklog_id = fields.Char(string='Worklog ID', ondelete='cascade')


class JiraProjectConnector(models.Model):
    _name = "jira.project.connector"

    jira_project_ids = fields.Many2many(
        'jira.project',
        'jira_project_connector_jira_project_rel',
        'jira_project_connector_id',
        'jira_project_id',
        string="Jira Project")
    # 'openproject_id =  fields.Many2one('openproject_project', string="Openproject Project"),
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    status = fields.Selection([
        ('success', 'Success'),
        ('error', 'Error'),
    ], string="Status")
    worklog_ids = fields.One2many('jira.worklog',
                                  'jira_project_connector_id',
                                  string='Worklog',
                                  copy=True)
    invoice_id = fields.Many2one('account.invoice',
                                 string='Account Invoice')
    jira_user_id = fields.Many2one('jira.project.conf',
                                   string='Jira User')

    @api.multi
    def decode_jira_time(self, string):

        day = hour = minute = '0'
        timing = string.split(' ')
        if len(timing) == 1:
            if len(timing[0]) == 2:
                if timing[0][1] == 'd':
                    day = timing[0][0]
                elif timing[0][1] == 'h':
                    hour = timing[0][0]
                elif timing[0][1] == 'm':
                    minute = '0' + timing[0][0]
            elif len(timing[0]) == 3:
                if timing[0][2] == 'd':
                    day = '%s%s' % (timing[0][0], timing[0][1])
                elif timing[0][2] == 'h':
                    hour = '%s%s' % (timing[0][0], timing[0][1])
                elif timing[0][2] == 'm':
                    minute = '%s%s' % (timing[0][0], timing[0][1])
        elif len(timing) == 2:
            for t in timing:
                if len(t) == 2:
                    if t[1] == 'd':
                        day = t[0]
                    elif t[1] == 'h':
                        hour = t[0]
                    elif t[1] == 'm':
                        minute = '0' + t[0]
                elif len(t) == 3:
                    if t[2] == 'd':
                        day = '%s%s' % (t[0], t[1])
                    elif t[2] == 'h':
                        hour = '%s%s' % (t[0], t[1])
                    elif t[2] == 'm':
                        minute = '%s%s' % (t[0], t[1])
        elif len(timing) == 3:
            for t in timing:
                if len(t) == 2:
                    if t[1] == 'd':
                        day = t[0]
                    elif t[1] == 'h':
                        hour = t[0]
                    elif t[1] == 'm':
                        minute = '0' + t[0]
                elif len(t) == 3:
                    if t[2] == 'd':
                        day = '%s%s' % (t[0], t[1])
                    elif t[2] == 'h':
                        hour = '%s%s' % (t[0], t[1])
                    elif t[2] == 'm':
                        minute = '%s%s' % (t[0], t[1])
        if day:
            hour = str(int(hour) + int(day) * 8)
        if minute == '0':
            minute = '00'
        value = '%s:%s' % (hour, minute)
        return value

    @api.multi
    def decode_jira_create_time(self, string, start, end):
        date_dict = string.split('T')
        correct = False
        if date_dict:
            today_date = date_dict[0]
            date_time = datetime.strptime(today_date, "%Y-%m-%d").date()
            start = datetime.strptime(start, "%Y-%m-%d").date()
            end = datetime.strptime(end, "%Y-%m-%d").date()
            if start <= date_time <= end:
                correct = True
                return {'correct': correct, 'time': today_date}
        return {'correct': correct}

    @api.model
    def create(self, values):
        jira_project_connector = super(
            JiraProjectConnector, self).create(values)
        if values.get('jira_project_ids') \
                and values.get('jira_project_ids')[0] \
                and values.get('jira_project_ids')[0][2]:
            jira_project_ids = values.get('jira_project_ids')[0][2]

            employee_pool = self.env['hr.employee']
            contract_pool = self.env['hr.contract']
            customer = self.env['res.partner'].search(
                [('name', '=', 'Bytebrand Solutions GmbH')])
            if not customer:
                raise UserError(_('You do not have customer '
                                  'Bytebrand Solutions GmbH'))

            currency = self.env['res.currency'].search([('name', '=', 'USD')])
            account = self.env['account.account'].search(
                [('code', '=', 'ASS_REC')])
            pr_account = self.env['account.account'].search(
                [('code', '=', 'ACC_SER')])
            if not account or not pr_account:
                raise UserError(_('You do not have account ASS_REC or ACC_SER'))

            invoice = self.env['account.invoice'].create({
                'partner_id': customer[0].id,
                'date_invoice': date.today(),
                'currency_id': currency[0].id,
                'account_id': account[0].id,
            })

            account_invoice_line_pool = self.pool.get('account.invoice.line')
            jira_user = self.env['jira.project.conf'].browse(
                values.get('jira_user_id'))
            product_id = jira_user.product_id.id
            hr_employee_category_pool = self.env['hr.employee.category']
            hr_employee_category_objects = hr_employee_category_pool.search(
                [('name', '=', 'Fulltime KG')])
            emails = [e.work_email
                      for e in hr_employee_category_objects[0].employee_ids]
            jira_project_objects = self.env['jira.project'].browse(
                jira_project_ids)
            for jira_project_obj in jira_project_objects:
                auth = (jira_user.name, jira_user.password)
                content = requests.get(
                    'https://kindgeek.atlassian.net/rest/api/2/search?jql=project=%s&maxResults=1000' % jira_project_obj.key,
                    auth=auth)
                d = json.loads(content.content)
                jira_worklog_objects = []
                for i in d.get('issues'):
                    content = requests.get(
                        'https://kindgeek.atlassian.net/rest/api/2/issue/%s/worklog' % i.get(
                            'key'),
                        auth=auth)
                    d = json.loads(content.content)
                    for w in d.get('worklogs'):

                        time_log = self.decode_jira_create_time(
                            str(w.get('created')),
                            values.get('start_date'),
                            values.get('end_date')),

                        if time_log[0] and time_log[0].get('correct') \
                                and str(w.get('author').get(
                                    'emailAddress')) in emails:
                            vals = {
                                'jira_project_connector_id':
                                    jira_project_connector.id,
                                'email':
                                    str(w.get('author').get('emailAddress')),
                                'time': self.decode_jira_time(
                                    str(w.get('timeSpent'))),
                                'task_key': str(i.get('key')),
                                'time_log': time_log[0].get('time'),
                                'author':
                                    str(w.get('author').get('displayName')),
                                'worklog_id': str(w.get('id')),
                                'project': jira_project_obj.name
                            }
                            worklog_id = self.env['jira.worklog'].create(vals)
                            jira_worklog_objects.append(worklog_id)

                employee_mails = []
                for jira_worklog_object in jira_worklog_objects:
                    if jira_worklog_object.email not in employee_mails:
                        employee_mails.append(jira_worklog_object.email)
                employee_wages = {}
                for employee_mail in employee_mails:
                    employee = employee_pool.search(
                        [('work_email', '=', employee_mail)])
                    try:
                        employee = employee[0]
                    except:
                        pass
                    contract_object = contract_pool.search(
                        [('employee_id', '=', employee.id)])
                    employee_wages[employee_mail] = contract_object.wage

                for employee_mail in employee_mails:
                    line_values = {}
                    hour = minute = 0
                    for jira_worklog_object in jira_worklog_objects:
                        if jira_worklog_object.email == employee_mail:
                            time = jira_worklog_object.time
                            time = time.split(':')
                            hour += int(time[0])
                            minute += int(time[1])

                    employee_time = hour + minute / 60
                    employee_wage = employee_time * employee_wages.get(
                        employee_mail) / 161

                    description = '%s, %s' % (
                        jira_project_obj.name, employee_mail)

                    line_values.update(invoice_id=invoice.id,
                                       product_id=product_id,
                                       partner_id=customer[0].id,
                                       quantity=1,
                                       currency_id=currency[0].id,
                                       price_unit=employee_wage,
                                       name=description,
                                       account_id=pr_account[0].id)
                    account_invoice_line_pool.create(line_values)
        else:
            raise UserError(_('You have to choose one or more projects'))

        jira_worklog_ids = self.env['jira.worklog'].search(
            [('jira_project_connector_id', '=', jira_project_connector.id)])
        if jira_worklog_ids:
            status = 'success'
        else:
            status = 'error'
        jira_project_connector.write(
            {'invoice_id': invoice.id, 'status': status})

        return jira_project_connector

    @api.multi
    def write(self, vals):
        print '<<<<<<<<<<<<<<<<<<<<<<<<WRITE>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
        return super(JiraProjectConnector, self).write(vals)
