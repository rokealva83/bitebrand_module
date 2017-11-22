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
from datetime import datetime, date
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import logging

_logger = logging.getLogger(__name__)

STATES = (
    ('draft', 'Draft'),
    ('storage', 'Storage'),
    ('reserve', 'Reserve'),
    ('issued', 'Issued'),
    ('repair', 'Repair'),
    ('on_cancellation', 'On Cancellation'),
    ('cancellation', 'Cancellation'),
)
TYPE_TECHNIQUE = (
    ('pc', 'PC'),
    ('notebook', 'Notebook'),
    ('monitor', 'Monitor'),
    ('headset', 'Headset'),
    ('mobile', 'Mobile'),
    ('keyboard', 'Keyboard'),
    ('mouse', 'Mouse'),
    ('storage', 'Storage'),
    ('server', 'Server'),
    ('commutator', 'Commutator'),
    ('switch', 'Switch'),
    ('network', 'Network'),
    ('printer', 'Printer'),
)


class HrTechnique(models.Model):
    _name = "hr.technique"
    _description = "Employee Equipment"
    # _order = 'name'

    name = fields.Char(string='Name',
                       size=256,
                       required=True)
    state = fields.Selection(STATES,
                             string='State',
                             default='storage')
    type = fields.Many2one('hr.technique.type',
                           string='Type',
                           required=True)
    employee_id = fields.Many2one('hr.employee',
                                  string='Employee')
    date_of_issue = fields.Date(string='Date Of Issue')
    date_of_purchase = fields.Date(string='Date Of Purchase',
                                   required=True)
    cash = fields.Float(string='Cash',
                        required=True)
    serial_number = fields.Char(string='Serial number',
                                size=256,
                                required=True)
    inventory_number = fields.Char(string='Inventory Number',
                                   size=256,
                                   required=True)
    description = fields.Char(string='Description',
                              size=256,
                              required=True)

    cause_of_repair = fields.Text(string='Cause Of Repair',
                                  states={
                                      'cancellation': [('readonly', True)],
                                      'on_cancellation': [('readonly', True)],
                                      'repair': [('readonly', True)], })

    venue_repair = fields.Text(string='Venue Repair',
                               states={
                                   'cancellation': [('readonly', True)],
                                   'on_cancellation': [('readonly', True)],
                                   'repair': [('readonly', True)], })
    reason_for_cancellation = fields.Text(
        string='Reason For write-Off',
        states={'cancellation': [('readonly', True)],
                'on_cancellation': [('readonly', True)], })
    cancellation_act_number = fields.Char(
        string='Write-Off Act Number',
        size=256,
        states={'cancellation': [('readonly', True)],
                'on_cancellation': [('readonly', True)]})
    history_ids = fields.One2many('hr.technique.history',
                                  'technique_id',
                                  string='History',
                                  readonly=True)
    history_repair_ids = fields.One2many('hr.technique.history.repair',
                                         'technique_id',
                                         string='Repair History',
                                         readonly=True)
    comment_ids = fields.One2many(
        'hr.technique.comment',
        'technique_id',
        string='Comments',
        states={'cancellation': [('readonly', True)],
                'on_cancellation': [('readonly', True)]})

    cancellation_employee_send_ids = fields.Many2many(
        'hr.employee',
        'equipment_employee_cancellation_rel',
        'technique_id',
        'employee_id',
        string='Write-Off Employee Sender',
        states={'cancellation': [('readonly', True)]})

    cancellation_employee_ids = fields.One2many(
        'hr.technique.cancellation',
        'technique_id',
        string='Write-Off sender',
        states={'cancellation': [('readonly', True)]})

    @api.multi
    def save(self):
        context = self.env.context
        if context is None:
            context = {}
        print context
        if context.get('state'):
            return self.write({'state': context.get('state')})
        return False

    @api.multi
    def write(self, vals):
        errors = []
        for record in self:
            action = ''
            state = record.state
            next_state = vals.get('state')

            if vals.get('employee_id'):
                new_employee = self.env['hr.employee'].browse(
                    int(vals.get('employee_id')))
                if next_state == 'issued':
                    if record['employee_id']:
                        if record.employee_id.id != new_employee.id:
                            action = u'Issue: {old} -> {new}'.format(
                                old=record.employee_id.name,
                                new=new_employee.name)
                    else:
                        action = u'Issue: {new}'.format(
                            new=new_employee.name)
                if next_state == 'reserve':
                    if not (record.employee_id
                            and record.employee_id.id == new_employee.id):
                        action = u'Reserve: {new}'.format(
                            new=new_employee.name)

            if next_state in ('storage', 'on_cancellation', 'cancellation'):
                vals['employee_id'] = None

            if next_state != 'issued':
                vals['date_of_issue'] = None
            if next_state and state != next_state and not action:
                action = 'Transfer: {old} -> {new}'.format(
                    old=dict(STATES)[state], new=dict(STATES)[next_state])

            if next_state == 'repair':
                if not vals.get('cause_of_repair') \
                        and not record.cause_of_repair:
                    errors.append(' You must specify a reason for repair.')
                if not vals.get('venue_repair') and not record.venue_repair:
                    errors.append('You must specify the place of repair.')

            if next_state == 'on_cancellation':
                if not vals.get('reason_for_cancellation') \
                        and not record.reason_for_cancellation:
                    errors.append(
                        'You must specify a reason for the cancellation.')
                if not vals.get('cancellation_act_number') \
                        and not record.cancellation_act_number:
                    errors.append(
                        'It should specify the number of write-off act.')
                if not vals.get('cancellation_employee_send_ids') \
                        and not record.cancellation_employee_send_ids:
                    errors.append(
                        'It is necessary to form the commission to write-off.')

            if errors:
                raise ValidationError(
                    _(' '.join(errors)))

            if action:
                vals['history_ids'] = [(0, 0, {'name': action})]

                if state == 'repair' and next_state != state:
                    vals['history_repair_ids'] = [
                        (0, 0, {'name': record.venue_repair,
                                'cause_of_repair': record.cause_of_repair})]
                    vals['venue_repair'] = ''
                    vals['cause_of_repair'] = ''

        return super(HrTechnique, self).write(vals)


class HrTechniqueHistory(models.Model):
    _name = 'hr.technique.history'

    create_uid = fields.Many2one('res.users',
                                 string='Author',
                                 readonly=True)
    create_date = fields.Datetime(string='Create Date',
                                  readonly=True)
    name = fields.Char(string='Act',
                       size=256)
    state = fields.Char(string='Stage',
                        size=256)
    employee_id = fields.Integer(string='Employee')
    technique_id = fields.Many2one('hr.technique',
                                   string='Equipment')


HrTechniqueHistory()


class HrTechniqueHistoryRepair(models.Model):
    _name = 'hr.technique.history.repair'

    create_uid = fields.Many2one('res.users',
                                 string='Author',
                                 readonly=True)
    create_date = fields.Datetime(string='Create date',
                                  readonly=True)
    name = fields.Text(string='Venue Repair')
    cause_of_repair = fields.Text(string='Repair reason')
    technique_id = fields.Many2one('hr.technique',
                                   string='Equipment')


HrTechniqueHistoryRepair()


class HrTechniqueComment(models.Model):
    _name = 'hr.technique.comment'

    create_uid = fields.Many2one('res.users',
                                 string='Author',
                                 readonly=True)
    create_date = fields.Datetime(string='Create Date',
                                  readonly=True)
    name = fields.Text(string='Comments')
    technique_id = fields.Many2one('hr.technique',
                                   string='Equpment')


HrTechniqueComment()


class HrTechniqueCancellation(models.Model):
    _name = 'hr.technique.cancellation'
    _rec_name = 'employee_id'

    create_uid = fields.Many2one('res.users',
                                 string='Transfer',
                                 readonly=True)
    create_date = fields.Datetime(string='Create Date',
                                  readonly=True)
    employee_id = fields.Many2one('hr.employee',
                                  string='Employee')
    date_agree = fields.Datetime(string='Agree date')
    agree = fields.Boolean(string='Agree')
    technique_id = fields.Many2one('hr.technique',
                                   string='Equipment')

    @api.multi
    def save(self):
        self.write({'agree': True,
                    'date_agree': date.today().strftime(
                        DEFAULT_SERVER_DATETIME_FORMAT)})
        for record in self:
            if not self.search(
                    [('technique_id', '=', record.technique_id.id),
                     ('agree', '=', False)]):
                record.technique_id.write({'state': 'cancellation'})


HrTechniqueCancellation()


class HrTechniqueCancellation(models.Model):
    _name = 'hr.technique.type'

    name = fields.Char(string='Name')
    description = fields.Char(string='Description')
