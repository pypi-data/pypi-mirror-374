## -*- coding: utf-8 -*-
<%doc>

camcops_server/templates/test/test_template_filters.mako

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

<div>
    <h1>Testing Mako filtering:</h1>

    <table>
        <tr>
            <th>repr() | h</th>
            <th>| h</th>
            <th>| n</th>
            <th>default (no explicit) filter</th>
        </tr>
        %for test_string in test_strings:
            <tr>
                <td>${repr(test_string) | h}</td>
                <td>${test_string | h}</td>
                <td>${test_string | n}</td>
                <td>${test_string}</td>
            </tr>
        %endfor
    </table>

    <%namespace file="displayfunc.mako" import="one_per_line"/>

    <h2>one_per_line(), escaped</h2>
    <p>
        ${ one_per_line(["<span>Apple</span>", "Banana", "Carrot", 3.14159265359], escape=True ) | n}
    </p>
    <h2>one_per_line(), not escaped</h2>
    <p>
        ${ one_per_line(["<span>Apple</span>", "Banana", "Carrot", 3.14159265359], escape=False ) | n}
    </p>
</div>
