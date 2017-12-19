# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2017-2018 Flosslab http://www.flosslab.com
#    @authors
#       Andrea Peruzzu <andrea.peruzzu@flosslab.com>
#
#   About license see __openerp__.py
#
##############################################################################
from openerp import models, fields, api


class ResUsers(models.Model):

    _inherit = 'res.users'

    allowed_server_sharedmail_ids = fields.Many2many(
        'fetchmail.server',
        'fetchmail_server_sharedmail_user_rel', 'user_id', 'server_id',
        string='Fetchmail sharedmail servers allowed to be used')

