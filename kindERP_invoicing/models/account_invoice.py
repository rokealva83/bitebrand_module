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


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def _get_tax_amount_by_group(self):
        res = super(AccountInvoice, self)._get_tax_amount_by_group()
        try:
            res[0] = (u'MwSt.', res[0][1])
        except:
            if res:
                res[0] = ()
        return res

    project = fields.Char('Project')
    old_company = fields.Boolean(string='Old Company',
                                 default=False)


class AccountJournal(models.Model):
    _inherit = "account.journal"

    journal_bank_id = fields.Many2one('account.journal',
                                      required=True,
                                      string='Bank Journal',
                                      domain=[('type', '=', 'bank')])
