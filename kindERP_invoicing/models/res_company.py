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


class res_company(models.Model):
    _name = "res.company"
    _inherit = "res.company"

    owner = fields.Char(string='Owner')
    b_name = fields.Char(string='Name')
    b_street = fields.Char(string='Street')
    b_zip = fields.Char(string='Zip')
    b_city = fields.Char(string='City')
    b_country = fields.Many2one('res.country',
                                string='Country')
    b_phone = fields.Char(string='Phone')
    b_bic = fields.Char(string='Bank Identifier Code',
                        select=True,
                        help="Sometimes called BIC or Swift.")
    b_mwst = fields.Char(string='MwSt Nummer')
