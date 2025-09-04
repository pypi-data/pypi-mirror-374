## -*- coding: utf-8 -*-
<%doc>

camcops_server/templates/menu/groups_view.mako

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

<%inherit file="base_web.mako"/>

<%!
from camcops_server.cc_modules.cc_pyramid import Icons, Routes
%>

<%include file="db_user_info.mako"/>

<h1>
    ${ req.icon_text(
        icon=Icons.GROUPS,
        text=_("Groups")
    ) | n }
</h1>

<%include file="groups_table.mako" args="groups_page=groups_page, valid_which_idnums=valid_which_idnums, with_edit=True"/>

<div>
    ${ req.icon_text(
        icon=Icons.GROUP_ADD,
        url=request.route_url(Routes.ADD_GROUP),
        text=_("Add a group")
    ) | n }
</div>

<%include file="to_main_menu.mako"/>
