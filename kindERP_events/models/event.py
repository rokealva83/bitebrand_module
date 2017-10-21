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
from odoo.exceptions import UserError


class EventEvent(models.Model):
    """Event"""
    _inherit = 'event.event'

    @api.multi
    def get_registered_user(self):
        employee_pool = self.env['hr.employee']
        employee_id = employee_pool.search(
            [('user_id', '=', self.env.user.id)])
        for registration_id in self.registration_ids:
            if employee_id == registration_id.employee_id:
                if registration_id.state != 'draft':
                    self.user_registered = True
                else:
                    self.user_registered = False

    @api.multi
    def registration_from_event(self):
        event_registration_pool = self.env['event.registration']
        employee_pool = self.env['hr.employee']
        employee_id = employee_pool.search([('user_id', '=', self.env.user.id)])

        if not employee_id:
            raise UserError(_('You mast have related employee'))
        employee_registered = event_registration_pool.search(
            [('employee_id', '=', employee_id.id),
             ('event_id', '=', self.id)])
        if not employee_registered:
            values = {
                'event_id': self.id,
                'partner_id': self.env.user.partner_id.id,
                'employee_id': employee_id.id,
                'state': 'open',
                'email': employee_id.work_email,
                'phone': employee_id.mobile_phone,
                'name': employee_id.name,
            }
            event_registration_pool.create(values)
        elif employee_registered.state == 'draft':
            employee_registered.write({'state': 'open'})
            self.slack_send_message('add_user')
        else:
            employee_registered.write({'state': 'draft'})
            self.slack_send_message('remove_user')

    user_registered = fields.Boolean(compute='get_registered_user',
                                     string='Registered User')
    description = fields.Html(string='Event Description')
    only_bb = fields.Boolean(string='Only BB')
    check_user = fields.Boolean(string='Check')
    date_end = fields.Datetime(string='End Date',
                               track_visibility='onchange',
                               states={'done': [('readonly', True)]})

    @api.one
    def button_confirm(self):
        self.state = 'confirm'
        self.slack_send_message('create')

    @api.multi
    def slack_send_message(self, type):
        slack_bot_message = self.env['slack.bot.message'].search(
            [('type', '=', type)])
        if slack_bot_message:
            if len(slack_bot_message) > 1:
                slack_bot_message = slack_bot_message[0]
            link = ''
            if slack_bot_message.link:
                link = 'http://erp.bytebrand.net/web?#id=%s&view_type=form&model=event.event&menu_id=204&action=274' % self.id
            message = '%s \n %s' % (slack_bot_message.message, link)
            self.env['slack.bot'].send_message(self, message)

    @api.multi
    def send_invite(self):
        employee_pool = self.env['hr.employee']
        if self.only_bb:
            employees = employee_pool.search([])
            employee_category_pool = self.env['hr.employee.category']
            employee_category = employee_category_pool.search(
                [('name', '=', 'Fulltime BB')])
            for employee in employees:
                if employee_category in employee.category_ids:
                    values = {
                        'mail_from': employee.id,
                        'mail_to': employee.work_email,
                        'mail_reply_to': '',
                        'subject': self.name,
                        'body': self.description,
                    }
                    message = self.env['create.message.wizard'].create(values)
                    if message:
                        message.send_message()
        else:
            for employee in employee_pool.search([]):
                values = {
                    'mail_from': employee.id,
                    'mail_to': employee.work_email,
                    'mail_reply_to': '',
                    'subject': self.name,
                    'body': self.description,
                }
                message = self.env['create.message.wizard'].create(values)
                if message:
                    message.send_message()


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    employee_id = fields.Many2one(
        'hr.employee', string='Employee',
        states={'done': [('readonly', True)]})

    @api.model
    def create(self, values):
        event_registration = super(EventRegistration, self).create(values)
        message = 'Yeh! \n New employee %s attend our event %s' % (
            event_registration.employee_id.name,
            event_registration.event_id.name)
        self.env['slack.bot'].send_message(event_registration.event_id, message)
        template_name = 'Event Registration'
        mail_notification(event_registration, template_name)


class EventType(models.Model):
    _name = 'event.type'

    name = fields.Char(string='Name')


@api.multi
def mail_notification(obj, template_name):
    email_template_pool = obj.env['mail.template']
    template_id = email_template_pool.search([('name', '=', template_name)])
    mail_id = obj.pool['mail.template'].send_mail(
        obj.env.cr, obj.env.uid, template_id.id, obj.id, force_send=True,
        context=obj.env.context)
    return mail_id
