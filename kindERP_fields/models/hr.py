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
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.model
    def default_get(self, fields):
        res = super(HrEmployee, self).default_get(fields)
        res.update(check_owner_user = True,
                   check_group_user = True)
        return res

    @api.multi
    def _check_owner_user(self):
        res_groups_pool = self.env['res.groups']
        groups = res_groups_pool.search([
            ('full_name', 'in',
             ['Human Resources / Manager', 'Human Resources / Officer'])])
        groups_ids = [g.id for g in groups]
        if self:
            for data in self:

                if self.env.uid == 1:
                    data.check_owner_user = True
                    data.check_group_user = True
                else:
                    data.check_owner_user = False
                    data.check_group_user = False

                    if data.user_id.id == self.env.uid:
                        data.check_owner_user = True
                    if self.env.user in self.env['res.users'].search(
                            [('groups_id', 'in', groups_ids)]):
                        data.check_group_user = True

        else:
            for data in self:
                data.check_owner_user = True
                data.check_group_user = True

    address_home_id = fields.Char(string='Home Address')

    secondary_phone = fields.Char(string='Secondary Phone')
    personal_email = fields.Char(string='Personal Email')
    skype = fields.Char(string='Skype')
    jira = fields.Char(string='Jira')
    bitbucket = fields.Char(string='Bitbucket')
    github = fields.Char(string='Github')
    gitlab = fields.Char(string='Gitlab')

    last_name_ua = fields.Char(string='First Name')
    first_name_ua = fields.Char(string='Second Name')
    second_name_ua = fields.Char(string='Surname')
    contract_number = fields.Char(string='Contract Number')
    key_card_number = fields.Char(string='Key Card Number')

    attachment_ids = fields.One2many(
        'ir.attachment',
        'res_id',
        string='Attachments',
        domain=[('res_model', '=', 'hr.employee')],
        context={'res_model': 'hr.employee'})

    technique_ids = fields.One2many(
        'hr.technique',
        'employee_id',
        string='Equipment',
        domain=[('state', 'in', ('draft', 'issued', 'reserve'))])

    check_owner_user = fields.Boolean(compute="_check_owner_user",
                                      string='Check owner user',)
    check_group_user = fields.Boolean(compute="_check_owner_user",
                                      string='Check group user')

    @api.multi
    def write(self, vals):
        for attachment in vals.get('attachment_ids', []):
            if attachment[0] == 0:
                attachment[2]['res_model'] = 'hr.employee'

        for record in self.read(['job_id']):
            if vals.get('job_id') and vals['job_id'] != record['job_id'] and \
                    record['job_id']:
                vals.update(
                    {'history_job_ids': [(0, 0, {
                        'res_model': 'employee.job.history',
                        'name': self.pool.get('hr.job').read(
                            vals['job_id'], ['name'])['name'],
                        'prev_value': record['job_id'][1], })],
                     'write_date': datetime.now()})

        return super(HrEmployee, self).write(vals)

    @api.multi
    def some_func(self, cr, uid, ids, context=None):

        invoices = self.env['account.invoice'].search(
            cr, uid, [('type', '=', 'out_invoice')])

        for invoice in invoices:
            if invoice.journal_id:
                journal = self.env['account.journal'].search(
                    [('type', '=', 'bank'),
                     ('currency_id', '=', invoice.journal_id.currency_id.id)])
                try:
                    journal = journal[0]
                except:
                    pass

                if journal:
                    values = {
                        'b_bic': journal.bank_acc_number,
                        'b_name': journal.bank_id.name,
                        'b_zip': journal.bank_id.zip,
                        'b_city': journal.bank_id.city,
                        'b_street': journal.bank_id.street, }
                    invoice.write(values)
