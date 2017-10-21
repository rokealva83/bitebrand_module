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
from slackclient import SlackClient


class SlackBot(models.Model):
    """Event"""
    _name = 'slack.bot'

    company_id = fields.Many2one('res.company', string='Company')
    name = fields.Char(string='Name')
    channel_ids = fields.Many2many('slack.channel',
                                   'slack_bot_channel_ref',
                                   'slack_bot_id',
                                   'channel_id',
                                   string='Channel')
    token = fields.Char(string='Token')
    only_bb = fields.Boolean(string='Only BB')

    @api.multi
    def send_message(self, event_object, message):
        if event_object.only_bb:
            slack_bots = self.search([('only_bb', '=', True)])
        else:
            slack_bots = self.search(
                [('company_id', '=', event_object.company_id.id)])
        if not slack_bots:
            slack_bots = self.search([])
        for bot in slack_bots:
            connect = SlackClient(bot.token)
            if connect.rtm_connect():
                for channel in bot.channel_ids:
                    channel = channel.name
                    message = message
                    connect.rtm_send_message(channel, message)
            else:
                print "Connection Failed, invalid token?"


class SlackChannel(models.Model):

    _name = 'slack.channel'

    name = fields.Char(string='Name')


class SlackBotMessage(models.Model):
    _name = 'slack.bot.message'

    type = fields.Selection([
        ('create', 'Create Event'),
        ('add_user', 'User Registration'),
        ('remove_user', 'User UnRegistration')],
        string='Type',
        require=True,
    )
    message = fields.Char(string='Message')
    link = fields.Boolean(string='Add Link')
