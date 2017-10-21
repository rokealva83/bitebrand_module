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


class Applicant(models.Model):
    _inherit = "hr.applicant"

    @api.multi
    def _get_attachment_number(self):
        for record in self:
            record.attachment_number = len(record.documents)

    attachment_number = fields.Integer(compute='_get_attachment_number',
                                       string="Number of Attachments")
    documents = fields.Many2many('ir.attachment',
                                 'rel_applicant_attachment'
                                 'applicant_id',
                                 'attachment_id',
                                 string="Documents")

    @api.multi
    def action_get_attachment_tree_view(self):
        attachment_action = self.env.ref('base.action_attachment')
        action = attachment_action.read()[0]
        action['context'] = {'default_res_model': self._name,
                             'default_res_id': self.ids[0]}
        need_document = [d.id for d in self.documents]
        print "<<< need_document >>> \n %s" % need_document
        action['domain'] = str([('id', 'in', need_document)])
        return action
