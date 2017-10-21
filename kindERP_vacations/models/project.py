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


class BytebrandProject(models.Model):
    _name = "bytebrand.project"
    _description = "Bytebrand Project"

    name = fields.Char(string="Name",
                       required=True)
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('process', 'In Process'),
                                        ('done', 'Done'),
                                        ('cancel', 'Cancel')],
                             string='State',
                             default='draft')
    description = fields.Text(string="Description",
                              required=True)
    team_lead_id = fields.Many2one('res.users', string="Team Lead",
                                   required=True)
    tech_lead_id = fields.Many2one('res.users', string="Tech Lead")
    employee_ids = fields.Many2many('hr.employee', string="Employees",
                                    required=True)

    @api.multi
    def action_process(self):
        self.write({'state': 'process'})

    @api.multi
    def action_done(self):
        self.write({'state': 'done'})

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})