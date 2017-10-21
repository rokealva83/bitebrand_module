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

from odoo import models, fields, api, _, tools
import logging

_logger = logging.getLogger(__name__)


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def default_get(self, fields):
        res = super(IrAttachment, self).default_get(fields)
        if not res.get('res_model') and res.get('res_id'):
            res.update(res_model=self.env.context.get('active_model'),
                       res_id=self.env.context.get('active_id'))
        return res

    @api.model
    def create(self, values):
        context = self.env.context
        attachment = super(IrAttachment, self).create(values)
        if context and context.get('active_model') == 'hr.applicant':
            applicant = self.env['hr.applicant'].browse(
                context.get('active_id'))
            if applicant:
                document_ids = ([d.id for d in applicant.documents]
                                + [attachment.id])
                applicant.documents = document_ids
                applicant.write({'documents': document_ids})
            if not self.res_model:
                attachment.write({'res_model': context.get('active_model'),
                                  'res_id': context.get('active_id')})
        return attachment


class HrApplicantWizard(models.Model):
    _name = "hr.applicant.wizard"

    @api.model
    def default_get(self, fields):
        res = super(HrApplicantWizard, self).default_get(fields)
        res.update(res_model=self.env.context.get('active_model'),
                   res_id=self.env.context.get('active_id'))
        return res

    attachment_id = fields.Many2one('ir.attachment', string="Attachment")
    res_model = fields.Char(string="Model")
    res_id = fields.Char(string="Res ID")

    @api.multi
    def add_attachment(self):
        applicant = self.env['hr.applicant'].browse(int(self.res_id))
        document_ids = ([d.id for d in applicant.documents])
        if self.attachment_id.id not in document_ids:
            document_ids += [self.attachment_id.id]
            applicant.documents = document_ids
            applicant.write({'documents': document_ids})
        return True
