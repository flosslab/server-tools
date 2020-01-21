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

from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import SUPERUSER_ID


class MailComposeMessage(osv.TransientModel):
    _inherit = 'mail.compose.message'

    def view_init(self, cr, uid, fields_list, context=None):
        if 'new_sharedmail_mail' in context and context['new_sharedmail_mail']:
            user_ids = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid)

            if len(user_ids.allowed_server_sharedmail_ids.ids) == 0:
                raise osv.except_osv(_('Warning!'), _("L'utente %s non e' associato a nessun Shared Mail Server") % user_ids.name)

            disabled_server_name = ""
            all_server_disabled = True
            for server in self.pool.get('fetchmail.server').browse(cr, SUPERUSER_ID, user_ids.allowed_server_sharedmail_ids.ids):
                if server.sharedmail == False:
                    disabled_server_name += server.name + " "
                else:
                    all_server_disabled = False
                    break
            if all_server_disabled:
                raise osv.except_osv(_('Warning!'),
                                     _("Nessuno dei server a cui è associato l'utente (%s) è abilitato in modalità Shared Mail Server") % disabled_server_name)

            pass

    def _get_def_server(self, cr, uid, context=None):
        res = self.pool.get('fetchmail.server').search(
            cr, uid, [('user_sharedmail_ids', 'in', uid), ('sharedmail', '=', True), ('state','=','done')], context=context)
        return res and res[0] or False

    _columns = {
        'server_sharedmail_id': fields.many2one('fetchmail.server', 'Server', domain="[('sharedmail', '=', True),('user_sharedmail_ids', 'in', uid),('state','=','done')]"),
    }
    _defaults = {
        'server_sharedmail_id': _get_def_server,
    }

    def send_mail(self, cr, uid, ids, context=None):
        """ Override of send_mail to duplicate attachments linked to the
        email.template.
            Indeed, basic mail.compose.message wizard duplicates attachments
            in mass
            mailing mode. But in 'single post' mode, attachments of an
            email template
            also have to be duplicated to avoid changing their ownership. """
        for wizard in self.browse(cr, uid, ids, context=context):
            if context.get('new_sharedmail_mail'):
                context['new_sharedmail_server_id'] = wizard.server_sharedmail_id.id
                for partner in wizard.partner_ids:
                    if not partner.email:
                        raise osv.except_osv(
                            _('Error'),
                            _('No mail for partner %s') % partner.name)
        return super(MailComposeMessage, self).send_mail(
            cr, uid, ids, context=context)

    def get_message_data(self, cr, uid, message_id, context=None):
        if not message_id:
            return {}
        if context is None:
            context = {}
        if context.get('reply_pec'):
            result = super(MailComposeMessage, self).get_message_data(
                cr, uid, message_id, context=context)
            # get partner_ids from action context
            partner_ids = context.get('default_partner_ids', [])
            # update the result
            result.update({
                'partner_ids': partner_ids,
            })
            return result
        else:
            return super(MailComposeMessage, self).get_message_data(
                cr, uid, message_id, context=context)

    # def get_record_data(self, cr, uid, values, context=None):
    #     """ Returns a defaults-like dict with initial values for the
    #     composition wizard when sending an email related a previous email
    #     (parent_id) or a document (model, res_id).
    #     This is based on previously computed default values. """
    #     if context is None:
    #         context = {}
    #     result = super(MailComposeMessage, self).get_record_data(
    #         cr, uid, values, context=context)
    #     if 'reply_pec' in context and context['reply_pec']:
    #         if 'parent_id' in values:
    #             parent = self.pool.get('mail.message').browse(
    #                 cr, uid, values.get('parent_id'), context=context)
    #             result['parent_id'] = parent.id
    #             subject = parent.subject
    #             re_prefix = _('Re:')
    #             if subject and not \
    #                     (subject.startswith('Re:') or
    #                      subject.startswith(re_prefix)):
    #                 subject = "%s %s" % (re_prefix, subject)
    #                 result['subject'] = subject
    #     return result
