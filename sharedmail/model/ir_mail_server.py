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

    def send_email(self, cr, uid, message, mail_server_id=None, smtp_server=None, smtp_port=None, smtp_user=None,
                   smtp_password=None, smtp_encryption=None, smtp_debug=False, context=None):
        server = self.browse(cr, uid, mail_server_id)
        if server.sharedmail:
            message['Return-Path'] = message.get('From')
        return super(IrMailServer, self).send_email(cr, uid, message, mail_server_id, smtp_server, smtp_port,
                                                      smtp_user, smtp_password, smtp_encryption, smtp_debug,
                                                      context=context)