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


class CreateMessageWizard(models.TransientModel):
    _name = 'create.message.wizard'
    _description = 'Create Message'

    mail_from = fields.Many2one('hr.employee', string='Mail From')
    mail_to = fields.Char(string='Mail To')
    mail_reply_to = fields.Char(string='Reply To')
    subject = fields.Char(string='Subject')
    body = fields.Html(string='Body')

    @api.multi
    def send_message(self):
        template_name = 'Event Invite'
        return mail_notification(self, template_name)


@api.multi
def mail_notification(obj, template_name):
    email_template_pool = obj.env['mail.template']
    template_id = email_template_pool.search([('name', '=', template_name)])
    mail_id = obj.pool['mail.template'].send_mail(
        obj.env.cr, obj.env.uid, template_id.id, obj.id, force_send=False,
        context=obj.env.context)
    mail = obj.env['mail.mail'].search([('id','=', mail_id)])
    obj.env['mail.mail'].send(mail)
    _logger.debug('Create a new message id = %s', mail_id)
    return mail_id
