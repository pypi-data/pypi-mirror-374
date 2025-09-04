## -*- coding: utf-8 -*-
<%doc>

camcops_server/templates/snippets/db_user_info.mako

===============================================================================

    Copyright (C) 2012, University of Cambridge, Department of Psychiatry.
    Created by Rudolf Cardinal (rnc1001@cam.ac.uk).

    This file is part of CamCOPS.

    CamCOPS is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    CamCOPS is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with CamCOPS. If not, see <https://www.gnu.org/licenses/>.

===============================================================================

</%doc>

<%page args="offer_main_menu=True"/>

<%!
from camcops_server.cc_modules.cc_pyramid import Icons, Routes
%>

<% _ = request.gettext %>

<div>
    ${ _("Database") }: <b>${ request.database_title }</b>.
    %if request.camcops_session.username:
        ${ _("Logged in as") } <b>${ request.camcops_session.username }</b>.
        [
            ${ req.icon_text(
                    icon=Icons.LOGOUT,
                    url=request.route_url(Routes.LOGOUT),
                    text=_("Log out")
            ) | n }
        %if offer_main_menu:
            |
            ${ req.icon_text(
                    icon=Icons.HOME,
                    url=request.route_url(Routes.HOME),
                    text=_("Main menu")
            ) | n }
        %endif
        ]
    %endif
</div>
