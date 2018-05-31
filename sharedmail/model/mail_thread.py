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
import email
import xmlrpclib

class MailThread(orm.Model):
    _inherit = 'mail.thread'

    def message_parse(self, cr, uid, message, save_original=False, context=None):
        if context is None:
            context = {}
        msg_dict = super(MailThread, self).message_parse(
            cr, uid, message, save_original=False,
            context=context)
        # author_id = self._FindOrCreatePartnersPec(
        #     cr, uid, message, message['From'], context=context)
        # if author_id:
        #     msg_dict['author_id'] = author_id
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
        res = super(MailThread, self).message_route(cr, uid, message, message_dict, model, thread_id, custom_values, context)
        if len(res) > 1:
            fetchmail_server_obj = self.pool.get('fetchmail.server')
            for alias_index, alias_item in enumerate(res):
                if alias_item[4]:
                    mail_alias = alias_item[4]
                if mail_alias.id:
                    fetchmail_server_ids = fetchmail_server_obj.search(cr, uid, [
                        ('sharedmail_account_alias', '=', mail_alias.id)], context=context)
                    fetchmail_server = fetchmail_server_obj.browse(cr, uid, fetchmail_server_ids)
                if fetchmail_server.id and 'fetchmail_server_id' in context and fetchmail_server.id == context[
                    'fetchmail_server_id']:
                    pass
                else:
                    res.pop(alias_index)
        return res

    def message_process(self, cr, uid, model, message, custom_values=None,
                        save_original=False, strip_attachments=False,
                        thread_id=None, context=None):
        if context is None:
            context = {}
        fetchmail_server_obj = self.pool.get('fetchmail.server')
        if fetchmail_server_obj.browse(cr, uid, context['fetchmail_server_id']).sharedmail:
            # extract message bytes - we are forced to pass the message as binary because
            # we don't know its encoding until we parse its headers and hence can't
            # convert it to utf-8 for transport between the mailgate script and here.
            if isinstance(message, xmlrpclib.Binary):
                message = str(message.data)
            # Warning: message_from_string doesn't always work correctly on unicode,
            # we must use utf-8 strings here :-(
            if isinstance(message, unicode):
                message = message.encode('utf-8')
            msg_txt = email.message_from_string(message)

            # parse the message, verify we are not in a loop by checking message_id is not duplicated
            msg = self.message_parse(cr, uid, msg_txt, save_original=save_original, context=context)
            if strip_attachments:
                msg.pop('attachments', None)

            # find possible routes for the message
            routes = self.message_route(cr, uid, msg_txt, msg, model, thread_id, custom_values, context=context)
            thread_id = self.message_route_process(cr, uid, msg_txt, msg, routes, context=context)
        else:
            return super(MailThread, self).message_process(cr, uid, model, message, custom_values, save_original, strip_attachments, thread_id, context)
        return thread_id

    # Impostando l'alias su TUTTI questa parte di codice non dovrebbe essere necessaria
    # def _FindPartnersPec(
    #     self, cr, uid, message=None, email_from=False, context=None
    # ):
    #     """
    #     create new method to search partner because
    #     the data of from  field of messagase is not found
    #     with _message_find_partners
    #     """
    #     res = False
    #     if email_from:
    #         partner_obj = self.pool.get('res.partner')
    #         partner_ids = partner_obj.search(
    #             cr, uid, [('pec_mail', '=', email_from.strip())],
    #             context=context)
    #         if partner_ids:
    #             res = partner_ids[0]
    #     return res
    #
    # def _FindOrCreatePartnersPec(
    #     self, cr, uid, message=None, pec_address=False, context=None
    # ):
    #     """
    #     searches for partner if it not exists creates it or returns admin ID
    #     """
    #     res = self._FindPartnersPec(
    #         cr, uid, message, pec_address, context=context)
    #     if res:
    #         return res
    #     else:
    #         if self.force_create_partner(cr, uid, context):
    #             return self.pool['res.partner'].create(
    #                 cr, SUPERUSER_ID,
    #                 {
    #                     'name': pec_address,
    #                     'pec_mail': pec_address
    #                 }, context=context)
    #         else:
    #             return SUPERUSER_ID