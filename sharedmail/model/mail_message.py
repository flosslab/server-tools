# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2017-2018 Flosslab http://www.flosslab.com
#    @authors
#       Andrea Peruzzu <andrea.peruzzu@flosslab.com>

#   About license see __openerp__.py
#
##############################################################################

from openerp.osv import fields, orm

import logging


_logger = logging.getLogger(__name__)


class MailMessage(orm.Model):
    _inherit = "mail.message"


    def _get_out_server_sharedmail(self, cr, uid, ids, name, args, context=None):
        res = {}
        if not context:
            context = {}
        for msg in self.browse(cr, uid, ids, context=context):
            res[msg.id] = False
            if msg.server_sharedmail_id:
                if msg.server_sharedmail_id.out_server_sharedmail_id:
                    res[msg.id] = msg.server_sharedmail_id.out_server_sharedmail_id[0].id
        return res

    def _get_mail_state(self,cr, uid, ids, name, args, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        res = dict.fromkeys(ids, False)
        for msg in self.browse(cr, uid, ids):
            mail_mail_obj = self.pool.get('mail.mail')
            mail_ids = mail_mail_obj.search(cr, uid, [('mail_message_id', '=', msg.id)])
            for mail in mail_mail_obj.browse(cr, uid, mail_ids):
                res[msg.id] = mail.state
        return res

    _columns = {
        'server_sharedmail_id': fields.many2one(
            'fetchmail.server', 'Server SharedMail', readonly=True),
        'out_server_sharedmail_id': fields.function(
            _get_out_server_sharedmail, type='many2one',
            relation='ir.mail_server',
            string='Related Outgoing Server'),
        'direction_sharedmail': fields.selection([
            ('in', 'in'),
            ('out', 'out'),
            ], 'Shared E-mail direction'),
        'sharedmail_type': fields.selection([
            ('sharedmail', 'Shared Mail'),
        ], 'SharedMail Type', readonly=True),
        'sharedmail_to': fields.text('A (SharedMail)', readonly=True),
        'sharedmail_cc': fields.text('CC (SharedMail)', readonly=True),
        'server_sharedmail_user': fields.related('server_sharedmail_id', 'user', type='char', readonly=True, string='Account (SharedMail)'),
        'server_sharedmail_state': fields.function(
            _get_mail_state, type='char',
            string='Mail State'),
        'mail_ids': fields.one2many('mail.mail', 'mail_message_id', 'Mails', readonly=True)
    }

    def _search(
        self, cr, uid, args, offset=0, limit=None, order=None,
        context=None, count=False, access_rights_uid=None
    ):
        if context is None:
            context = {}
        if context and context.has_key('fetchmail_server_id') and context['fetchmail_server_id']:
            fetchmail_server_obj = self.pool.get('fetchmail.server')
            fetchmail_server = fetchmail_server_obj.browse(cr, uid, context['fetchmail_server_id'])
            if fetchmail_server.sharedmail:
                args.append(('server_sharedmail_id', '=', context['fetchmail_server_id']))
        if context.get('sharedmail_messages'):
            return super(orm.Model, self)._search(
                cr, uid, args, offset=offset, limit=limit, order=order,
                context=context, count=count,
                access_rights_uid=access_rights_uid)
        else:
            return super(MailMessage, self)._search(
                cr, uid, args, offset=offset, limit=limit, order=order,
                context=context, count=count,
                access_rights_uid=access_rights_uid)

    def check_access_rule(self, cr, uid, ids, operation, context=None):
        if context is None:
            context = {}

        cr.execute('SELECT DISTINCT id, model, res_id, server_sharedmail_id FROM "%s" WHERE id = ANY (%%s)' % self._table, (ids,))
        for id, rmod, rid, server_sharedmail_id in cr.fetchall():
            if server_sharedmail_id:
                return super(orm.Model, self).check_access_rule(
                    cr, uid, ids, operation, context=context)
        return super(MailMessage, self).check_access_rule(
            cr, uid, ids, operation, context=context)

    def create(self, cr, uid, values, context=None):
        if context is None:
            context = {}
        if 'author_id' in values and values['author_id'] == 1:
            values['author_id'] = False
        res = super(MailMessage, self).create(cr, uid, values, context=context)
        return res