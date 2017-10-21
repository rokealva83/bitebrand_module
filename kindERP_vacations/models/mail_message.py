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
from datetime import date
import logging

_logger = logging.getLogger(__name__)


class Message(models.Model):
    _inherit = 'mail.message'

    message_date = fields.Char('Date', default='')
    date_from = fields.Char('Date From', default='')
    date_to = fields.Char('Date To', default='')
    partner_name = fields.Char('Partner Name', default='')
    status = fields.Char('Status', default='')

    @api.model
    def create(self, values):
        if values.get('model') == 'hr.holidays':
            hr_holidays = self.env['hr.holidays'].browse(values.get('res_id'))
            values['message_date'] = date.today()
            values['partner_name'] = hr_holidays.employee_id.name
            values['status'] = hr_holidays.holiday_status_id.name
            if hr_holidays.date_from:
                values['date_from'] = hr_holidays.date_from.split(' ')[0]
            if hr_holidays.date_to:
                values['date_to'] = hr_holidays.date_to.split(' ')[0]

        return super(Message, self).create(values)
