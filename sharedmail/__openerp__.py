# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2017-2018 Flosslab http://www.flosslab.com
#    @authors
#       Andrea Peruzzu <andrea.peruzzu@flosslab.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Shared Mail",
    "version": "8.0.1.8.10",
    "author": "Flosslab Srl",
    "category": "Tools",
    "website": "http://www.flosslab.com",
    "license": "AGPL-3",
    "depends": [
        "fetchmail",
        "mail",
        "contacts"
    ],
    "data": [
        "security/mail_data.xml",
        "view/fetchmail_view.xml",
        "view/ir_mail_server.xml",
        "wizard/mail_compose_message_view.xml",
        "view/mail_view.xml",
        "view/res_users.xml",
        "security/ir.model.access.csv"
    ],
    "demo": [
        "demo/sharedmail_data.xml"
    ],
    "installable": True
}
