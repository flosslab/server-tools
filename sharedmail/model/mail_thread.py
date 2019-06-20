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

from openerp.osv import orm
from openerp import api
from openerp.addons.mail.mail_message import decode
import email
import xmlrpclib

def decode_header(message, header, separator=' '):
    return separator.join(map(decode, filter(None, message.get_all(header, []))))

class MailThread(orm.Model):
    _inherit = 'mail.thread'

    def message_parse(self, cr, uid, message, save_original=False, context=None):
        if context is None:
            context = {}
        msg_dict = super(MailThread, self).message_parse(cr, uid, message, save_original=save_original, context=context)
        server = self.pool.get('fetchmail.server').browse(cr, uid, context.get('fetchmail_server_id'))
        if server.sharedmail:
            msg_dict['server_sharedmail_id'] = context.get('fetchmail_server_id')
            msg_dict['sharedmail_type'] = "sharedmail"
            msg_dict['direction_sharedmail'] = "in"
            msg_dict['sharedmail_state'] = "new"
        return msg_dict

    @api.cr_uid_ids_context
    def message_post(self, cr, uid, thread_id, body='',
                     subject=None, type='notification',
                     subtype=None, parent_id=False,
                     attachments=None, context=None,
                     content_subtype='html', **kwargs):
        if not context:
            context = {}
        if 'reply_sharedmail' in context and context['reply_sharedmail']:
            return super(MailThread, self).message_post(
                cr, uid, 0, body=body,
                subject=subject, type=type,
                subtype=subtype, parent_id=parent_id,
                attachments=attachments, context=context,
                content_subtype=content_subtype, **kwargs)

        msg_id = super(MailThread, self).message_post(
            cr, uid, thread_id, body=body,
            subject=subject, type=type,
            subtype=subtype, parent_id=parent_id,
            attachments=attachments, context=context,
            content_subtype=content_subtype, **kwargs)

        msg_obj = self.pool.get('mail.message')
        msg = msg_obj.browse(cr, uid, msg_id)
        if msg.sharedmail_type == 'sharedmail':
            vals = {}
            if 'to' in kwargs and kwargs['to']:
                vals = {'sharedmail_to': kwargs['to']}
            if 'cc' in kwargs and kwargs['cc']:
                vals.update({'sharedmail_cc': kwargs['cc']})
            if len(vals):
                msg_obj.write(cr, uid, msg_id, vals)
        return msg_id

    def message_route(self, cr, uid, message, message_dict, model=None, thread_id=None,
                      custom_values=None, context=None):
        #self.fix_headers_bounces(message)
        res = super(MailThread, self).message_route(cr, uid, message, message_dict, model, thread_id, custom_values, context)
        if context and context.has_key('fetchmail_server_id') and context['fetchmail_server_id']:
            fetchmail_server_obj = self.pool.get('fetchmail.server')
            fetchmail_server = fetchmail_server_obj.browse(cr, uid, context['fetchmail_server_id'])
            if fetchmail_server.sharedmail:
                new_res = []
                for route in res:
                    mail_alias = None
                    if route[4]:
                        mail_alias = route[4]
                    if mail_alias and mail_alias.id:
                        fetchmail_server_ids = fetchmail_server_obj.search(cr, uid, [
                            ('sharedmail_account_alias', '=', mail_alias.id)
                        ], context=context)
                        sharedmail_fetchmail_servers = fetchmail_server_obj.browse(cr, uid, fetchmail_server_ids)
                        for sharedmail_fetchmail_server in sharedmail_fetchmail_servers:
                            if fetchmail_server.id == sharedmail_fetchmail_server.id:
                                new_res.append(route)
                    else:
                        new_res.append(route)
                return new_res
        return res

    # modifica due campi nelle notifiche di errore dei server di legalmail che diversamente verrebbero scartate dal sistema
    def fix_headers_bounces(self, message):
        email_from = decode_header(message, 'From')
        if email_from and email_from.lower().__contains__("mailer-daemon@"):
            fake_from = ('From', message['From'].lower().replace('mailer-daemon', 'mailerdaemon'))
            message._headers = [i for i in message._headers if not i[0] == 'From']
            message._headers.append(fake_from)
        if message.get_content_type() == 'multipart/report':
            fake_content_type = ('Content-Type', message['Content-Type'].replace('Report', 'Mixed').replace('report', 'mixed'))
            message._headers = [i for i in message._headers if not i[0] == 'Content-Type']
            message._headers.append(fake_content_type)
        return message