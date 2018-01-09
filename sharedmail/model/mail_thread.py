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
        msg_dict['server_sharedmail_id'] = context.get('fetchmail_server_id')
        msg_dict['sharedmail_type'] = "sharedmail"
        return msg_dict

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