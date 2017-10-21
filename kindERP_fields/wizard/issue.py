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

    technique_id = fields.Many2one('hr.technique',
                                   'Equipment')
    employee_id = fields.Many2one('hr.employee',
                                  'Employee',
                                  required=True)
    state = fields.Char('State',
                        size=256)

    # _defaults = {
    #     'technique_id': lambda cr, u, i, ctx: ctx.get('technique_id'),
    #     'state': lambda cr, u, i, ctx: ctx.get('state'),
    #     'employee_id': lambda cr, u, i, ctx: ctx.get('employee_id'),
    # }

    @api.multi
    def set_issue(self):
        for record in self.read([]):
            employee = self.pool.get('hr.employee').read(
                record['employee_id'][0], ['department_id'])
            self.env['hr.technique'].browse(record['technique_id'][0]).write(
                {'state': record['state'],
                 'employee_id': record['employee_id'][0],
                 'date_of_issue': datetime.date.today().strftime("%Y/%m/%d"),
                 'department_id':
                     employee['department_id'][0]
                     if employee['department_id'] else None})
        return {'type': 'ir.actions.act_window_close'}


Issue()
