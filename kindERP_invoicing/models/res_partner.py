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


class ResPartner(models.Model):
    _inherit = "res.partner"

    employee_id = fields.Many2one('hr.employee',
                                  string='Employee')


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    agreement = fields.Char(string='Actual Agreement')
    agreement_date = fields.Date(string='Agreement Date')

    old_agreement = fields.Char(string="Old Agreement")
    old_agreement_date = fields.Date(string='Old Agreement Date')

    owner = fields.Char(string='Owner')
    tax_code = fields.Char(string='Personal Tax Number')
    beneficiary = fields.Char(string='Beneficiary')
    account = fields.Char(string='Account Number')
    iban = fields.Char(string='IBAN')
    iban_code = fields.Char(string='IBAN Code')
    beneficiary_bank = fields.Char(string='Beneficiary’s bank')
    beneficiary_bank_address = fields.Char(string='Beneficiary’s bank address')
    swift_code = fields.Char(string='SWIFT code')
    corespondent_bank = fields.Char(string='Corespondent bank')
    swift_code_corespondent = fields.Char(string='SWIFT code Corespondent')
    corespondent_account = fields.Char(string='Corespondent account')
