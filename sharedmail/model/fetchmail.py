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

from openerp import models, fields


class FetchmailServer(models.Model):

    _inherit = "fetchmail.server"

    sharedmail = fields.Boolean(
        "Account Shared Mail",
        help="Check if this server is Shared Mail")

    user_sharedmail_ids = fields.Many2many(
        'res.users',
        'fetchmail_server_sharedmail_user_rel', 'server_id', 'user_id',
        string='Users allowed to use this sharedmail server')

    out_server_sharedmail_id = fields.One2many(
        'ir.mail_server',
        'in_server_sharedmail_id',
        string='Outgoing Shared Mail Server',
        readonly=True,
        copy=False)

    def get_fetch_server_sharedmail(self, cr, uid, context=None):
        server_ids = self.search(cr, uid, [('user_sharedmail_ids', '=', uid)])
        return server_ids