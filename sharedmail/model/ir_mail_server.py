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


class IrMailServer(models.Model):

    _inherit = "ir.mail_server"

    in_server_sharedmail_id = fields.Many2one(
        'fetchmail.server',
        string='Incoming Shared Mail server')

    sharedmail = fields.Boolean(
        "Account Shared Mail",
        help="Check if this server is Shared Mail")

    _sql_constraints = [
        ('incomingserver_name_unique', 'unique(in_server_sharedmail_id)',
         'Incoming Server already in use'),
        ]

    def get_mail_server_sharedmail(self, cr, uid, fetch_server_id, context=None):
        mail_server_obj = self.pool.get('ir.mail_server')
        mail_server_ids = mail_server_obj.search(cr, uid,
                                                 [('in_server_sharedmail_id',
                                                   '=',
                                                   fetch_server_id)]
                                                 )
        return mail_server_ids

