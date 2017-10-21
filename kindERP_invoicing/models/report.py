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

import base64
import logging

_logger = logging.getLogger(__name__)

class Report(models.Model):
    _name = "report"
    _inherit = "report"

    @api.model
    def _check_attachment_use(self, docids, report):
        """ Check attachment_use field. If set to true and an existing pdf is already saved, load
        this one now. Else, mark save it.
        """
        save_in_attachment = {}
        save_in_attachment['model'] = report.model
        save_in_attachment['loaded_documents'] = {}

        if report.attachment:
            records = self.env[report.model].browse(docids)
            filenames = self._attachment_filename(records, report)
            attachments = None
            if report.attachment_use:
                attachments = self._attachment_stored(records, report,
                                                      filenames=filenames)
            for record_id in docids:
                filename = filenames[record_id]

                # If the user has checked 'Reload from Attachment'
                if filename:
                    obj = self.pool[report.model].browse(record_id)
                    name_dict = filename.split('.')
                    filename = '%s-%s.%s' % (name_dict[0], obj.partner_id.name, name_dict[1])
                if attachments:
                    attachment = attachments[record_id]
                    if attachment:
                        # Add the loaded pdf in the loaded_documents list
                        pdf = attachment.datas
                        pdf = base64.decodestring(pdf)
                        save_in_attachment['loaded_documents'][record_id] = pdf
                        _logger.info(
                            'The PDF document %s was loaded from the database' % filename)

                        continue  # Do not save this document as we already ignore it

                # If the user has checked 'Save as Attachment Prefix'
                if filename is False:
                    # May be false if, for instance, the 'attachment' field contains a condition
                    # preventing to save the file.
                    continue
                else:
                    save_in_attachment[
                        record_id] = filename  # Mark current document to be saved

        return save_in_attachment
