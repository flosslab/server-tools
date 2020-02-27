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

    def default_get(self, cr, uid, fields, context=None):
        result = super(MailComposeMessage, self).default_get(cr, uid, fields, context=context)
        if context and context.get('new_sharedmail_mail', False):
            result['subject'] = False
        return result

    _columns = {
        'server_sharedmail_id': fields.many2one('fetchmail.server', 'Server', domain="[('sharedmail', '=', True),('user_sharedmail_ids', 'in', uid),('state','=','done')]"),
    }
    _defaults = {
        'model': 'res.partner',
        'res_id': lambda obj, cr, uid, context: uid,
        'server_sharedmail_id': _get_def_server,
    }

    def send_mail(self, cr, uid, ids, context=None):
        for wizard in self.browse(cr, uid, ids, context=context):
            if context.get('new_sharedmail_mail'):
                context['new_sharedmail_server_id'] = wizard.server_sharedmail_id.id
                for partner in wizard.partner_ids:
                    if not partner.email:
                        raise osv.except_osv(_('Error'), _('No mail for partner %s') % partner.name)
                # set template_id to False to avoid remove user_signature
                self.write(cr, uid, wizard.id, {'template_id': False}, context=context)
        return super(MailComposeMessage, self).send_mail(cr, uid, ids, context=context)

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

    def save_as_template(self, cr, uid, ids, context=None):
        result = super(MailComposeMessage, self).save_as_template(cr, uid, ids, context=context)

        if context and context.get('new_sharedmail_mail', False):
            model_data_obj = self.pool.get('ir.model.data')
            view_rec = model_data_obj.get_object_reference(cr, uid, 'sharedmail', 'email_compose_message_wizard_form_sharedmail')
            view_id = view_rec and view_rec[1] or False
            result['view_id'] = view_id

        return result