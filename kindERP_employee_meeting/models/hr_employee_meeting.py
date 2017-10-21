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
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class HrEmployeeMeeting(models.Model):
    _name = "hr.employee.meeting"
    _inherit = 'mail.thread'
    _description = "Employee Meeting"
    _rec_name = "employee_id"
    _order = 'id desc'

    state = fields.Selection(selection=[('draft', 'Upcoming'),
                                        ('confirm', 'Confirm'),
                                        ('done', 'Done')],
                             string='State',
                             default='draft')

    employee_id = fields.Many2one('hr.employee',
                                  string="Employee")
    employee_ids = fields.Many2many('hr.employee',
                                    'employee_meeting_rel',
                                    'meeting_id',
                                    'employee_id',
                                    string="Review Team",
                                    readonly=True,
                                    states={'draft': [('readonly', False)],
                                            'confirm': [('readonly', False)]}, )
    tech_employee_id = fields.Many2one(
        'hr.employee',
        string="Tech Review Employee",
        readonly=True,
        states={'draft': [('readonly', False)],
                'confirm': [('readonly', False)]}, )

    work_start_date = fields.Date(string="Work Start Date",
                                  readonly=True,
                                  states={'draft': [('readonly', False)]}, )

    review_date = fields.Datetime(string="Review Date")

    last_review_date = fields.Date(string="Last Review Date",
                                   readonly=True,
                                   states={'draft': [('readonly', False)]}, )

    employee_answer_ids = fields.One2many(
        'hr.employee.answer',
        'hr_employee_meeting_id',
        string="Question and answer",
        states={'done': [('readonly', True)]}, )
    resume = fields.Text(string=" Decision made by management",
                         readonly=True,
                         states={'confirm': [('readonly', False)]}, )
    comment = fields.Text(string="Technical Interview Results",
                          readonly=True,
                          states={'confirm': [('readonly', False)]}, )

    @api.multi
    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id.contract_ids:
            contract_id = self.employee_id.contract_ids[0]
            self.work_start_date = contract_id.date_start
        last_meetings = self.search([('employee_id', '=', self.employee_id.id)])
        self.review_date = datetime.now()
        if last_meetings:
            self.last_review_date = last_meetings[0].review_date
        else:
            self.last_review_date = None

    @api.multi
    def action_confirm(self):
        self.write({'state': 'confirm'})

    @api.multi
    def action_done(self):
        self.write({'state': 'done'})
        self.create({
            'employee_id': self.employee_id.id,
            'review_date': datetime.strptime(
                self.review_date.split(' ')[0].replace('-', ''),
                "%Y%m%d").date() + timedelta(days=90),
            'last_review_date': self.review_date,
            'employee_ids': [
                [6, False, [empl.id for empl in self.employee_ids]]],
            'tech_employee_id': self.tech_employee_id.id,
            'work_start_date': self.work_start_date,
        })

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.model
    def create(self, values):
        _logger.info('create')
        result = super(HrEmployeeMeeting, self).create(values)

        # self.check_followers(result)

        employee = self.env['hr.employee'].browse(values.get('employee_id'))
        _logger.info(employee)
        time_line = u'<p>Review meeting at <b>{date}</b> employee ' \
                    u'<b>{name}</b></p>'.format(
            date=result.review_date,
            name=employee.name)

        manager_line = ''
        if result.employee_ids:
            empl_name = ", ".join(
                [employee_id.name for employee_id in result.employee_ids])
            manager_line = u'<p><b>Review Team</b>: ' \
                           u'{empl_name}</p>'.format(empl_name=empl_name)
        tech_manager_line = ''
        if result.tech_employee_id:
            tech_manager_line = u'<p><b>Tech Interview Lead</b>: ' \
                                u'{empl_name}</p>'.format(
                empl_name=result.tech_employee_id.name)

        message_body = '<div>%s%s%s</div>' % (
            time_line, manager_line, tech_manager_line)

        message_values = {
            'body': message_body,
            'model': 'hr.employee.meeting',
            'res_id': result.id,
            'author_id': self.env.user.partner_id.id,
            'type': 'notification',
            'subject': False,
            'record_name': 'Meeting %s for %s' %
                           (values.get('review_date'), employee.name),
        }
        self.env['mail.message'].create(message_values)
        return result

    @api.multi
    def write(self, values):
        message_values = {'model': 'hr.employee.meeting',
                          'res_id': self.id,
                          'author_id': self.env.user.partner_id.id,
                          'type': 'notification',
                          'subject': False,
                          'record_name':
                              'Meeting %s for %s' %
                              (values.get('review_date') or self.review_date,
                               self.employee_id.name)}
        create_message = False
        if values.get('tech_employee_id'):
            old_tech_employee_id = self.tech_employee_id.name
            new_employee_name = self.env['hr.employee'].browse(
                values.get('tech_employee_id')).name
            message_values['body'] = '<div>Tech lead was changed:<p>' \
                                     ' <b>%s</b> to <b>%s</b></p></div>' % (
                                         old_tech_employee_id,
                                         new_employee_name)
            create_message = True

        if values.get('employee_ids'):
            old_managers = ", ".join(
                [employee_id.name for employee_id in self.employee_ids])
            new_employees = self.env['hr.employee'].browse(
                values.get('employee_ids')[0][2])
            new_managers = ", ".join(
                [employee_id.name for employee_id in new_employees])

            message_values['body'] = '<div>Review Team was changed:' \
                                     '<p><b>%s</b> to <b>%s</b></p></div>' % (
                                         old_managers, new_managers)
            create_message = True
        if values.get('state') == 'confirm':
            time_line = u'<b>{date} {time}</b>'.format(
                date=self.review_date.split(' ')[0],
                time=self.review_date.split(' ')[1])
            manager_line = ''
            if self.employee_ids:
                empl_name = ", ".join(
                    [employee_id.name for employee_id in self.employee_ids])
                manager_line = u'<p><b>Review Team</b>: ' \
                               u'{empl_name}</p>'.format(empl_name=empl_name)
            tech_manager_line = ''
            if self.tech_employee_id:
                tech_manager_line = u'<p><b>Tech Interview Lead</b>: ' \
                                    u'{empl_name}</p>'.format(
                    empl_name=self.tech_employee_id.name)
            message_values['body'] = \
                '<div>Confirmed review meeting for %s with %s with the ' \
                '%s%s</div>' % (
                    time_line, self.employee_id.name,
                    manager_line, tech_manager_line)
            create_message = True
        if values.get('state') == 'done':
            message_values['body'] = '<div>Review meeting was Done</div>'
            create_message = True
        res = super(HrEmployeeMeeting, self).write(values)

        if values.get('employee_ids') or values.get('tech_employee_id'):
            self.check_followers(self)
        if create_message:
            self.env['mail.message'].create(message_values)
        return res

    @api.multi
    def check_followers(self, meeting):
        followers = [meeting.employee_id.user_id]
        if meeting.tech_employee_id:
            if meeting.tech_employee_id.user_id not in followers:
                followers.append(meeting.tech_employee_id.user_id)
        if meeting.employee_ids:
            for empl in meeting.employee_ids:
                if empl.user_id not in followers:
                    followers.append(empl.user_id)
        if followers:
            follower_partners = [follower.partner_id
                                 for follower in
                                 meeting.message_follower_ids]
            message_follower_ids = []
            for user in followers:
                if user.partner_id not in follower_partners:
                    message_follower_ids += (
                        self.env['mail.followers']._add_follower_command(
                            self._name, [], {user.partner_id.id: None}, {},
                            force=True)[0])
            _logger.info(message_follower_ids)
            meeting.write({'message_follower_ids': message_follower_ids})
