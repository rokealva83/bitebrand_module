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
import datetime


class Issue(models.TransientModel):
    _name = 'hr.technique.issue'

    @api.model
    def default_get(self, fields):
        res = super(Issue, self).default_get(fields)
        res.update(technique_id=self.env.context.get('technique_id'),
                   state=self.env.context.get('state'),
                   employee_id=self.env.context.get('employee_id'))
        return res

    technique_id = fields.Many2one('hr.technique',
                                   string='Equipment')
    employee_id = fields.Many2one('hr.employee',
                                  string='Employee',
                                  required=True)
    state = fields.Char(string='State')

    @api.multi
    def set_issue(self):
        for record in self:
            self.env['hr.technique'].browse(record.technique_id.id).write(
                {'state': record.state,
                 'employee_id': record.employee_id.id,
                 'date_of_issue': datetime.date.today().strftime("%Y/%m/%d"),
                 'department_id': record.employee_id.department_id.id})
        return {'type': 'ir.actions.act_window_close'}


Issue()
