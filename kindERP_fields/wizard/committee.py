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


class HrCommittee(models.TransientModel):
    _name = 'hr.technique.committee'

    @api.model
    def default_get(self, fields):
        res = super(HrCommittee, self).default_get(fields)
        res.update(technique_id=self.env.context.get('technique_id'),
                   employee_id=self.env.context.get('employee_id'))
        return res

    technique_id = fields.Many2one('hr.technique',
                                   string='Equipment')
    employee_id = fields.Many2one('hr.employee',
                                  string='Employee',
                                  required=True)

    @api.multi
    def set_employee(self):
        for record in self.read([]):
            print record
            self.env['hr.technique'].browse(
                [record['technique_id'][0]], ).write(
                {'cancellation_employee_send_ids':
                     ((4, record['employee_id'][0]),),
                 'cancellation_employee_ids':
                     ((0, 0, {'employee_id': record['employee_id'][0]}),), })
            print '2'
        return {'type': 'ir.actions.act_window_close'}


HrCommittee()
