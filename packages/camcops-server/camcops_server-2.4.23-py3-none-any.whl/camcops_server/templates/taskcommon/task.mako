## -*- coding: utf-8 -*-
<%doc>

camcops_server/templates/taskcommon/task.mako

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

## <%page args="task: Task, viewtype: str, anonymise: bool, signature: bool, paged_media: bool, pdf_landscape: bool"/>

<%!

from cardinal_pythonlib.datetimefunc import format_datetime
from camcops_server.cc_modules.cc_constants import (
    CSS_PAGED_MEDIA,
    DateFormat,
    ERA_NOW,
)
from camcops_server.cc_modules.cc_html import (
    answer,
    get_yes_no,
)
from camcops_server.cc_modules.cc_pyramid import Icons, Routes, ViewArg, ViewParam
from camcops_server.cc_modules.cc_version_string import CAMCOPS_SERVER_VERSION_STRING

def inherit_file(context):
    ## https://groups.google.com/forum/#!topic/mako-discuss/okPBlbGhy_U
    viewtype = context['viewtype']
    if viewtype == ViewArg.HTML:
        return "base_web.mako"
    elif viewtype == ViewArg.PDF:
        if CSS_PAGED_MEDIA:
            pdf_landscape = context['pdf_landscape']
            if pdf_landscape:
                return "base_pdf_landscape.mako"
            else:
                return "base_pdf_portrait.mako"
        else:
            return "base_pdf_no_paged_media.mako"
    else:
        raise ValueError("This template is only for HTML/PDF views")

%>

<%inherit file="${ inherit_file(context) }"/>
## ... don't use "| n" for that.

## ============================================================================
## Title (overriding base.mako)
## ============================================================================

<%block name="title">
    <title>${ task.title_for_html(req, anonymise=anonymise) }</title>
</%block>

## ============================================================================
## For CSS paged media, extra headers
## ============================================================================

%if CSS_PAGED_MEDIA and viewtype == ViewArg.PDF:
    <%block name="extra_header_content">
        <%include file="task_page_header.mako" args="task=task, anonymise=anonymise"/>
    </%block>
    <%block name="extra_footer_content">
        <%include file="task_page_footer.mako" args="task=task"/>
    </%block>
%endif
## For non-paged media (i.e. wkhtmltopdf), the headers/footers are made separately.

## ============================================================================
## Task descriptive header: patient details, task details
## ============================================================================

<%include file="task_descriptive_header.mako" args="task=task, anonymise=anonymise"/>

## ============================================================================
## "Not current" warning and explanation (if applicable)
## ============================================================================

%if not task._current:
    <%include file="task_not_current.mako" args="task=task"/>
%endif

## ============================================================================
## "Invalid contents" warning (if applicable)
## ============================================================================

%if not task.field_contents_valid():
    <%include file="task_contents_invalid.mako" args="task=task"/>
%endif

## ============================================================================
## Special notes (if applicable)
## ============================================================================

%if task.special_notes:
    <%include file="special_notes.mako" args="special_notes=task.special_notes, title='TASK SPECIAL NOTES', viewtype=viewtype"/>
%endif

## ============================================================================
## Clinician
## ============================================================================

%if task.has_clinician:
    <%include file="clinician.mako" args="task=task"/>
%endif

## ============================================================================
## Respondent
## ============================================================================

%if task.has_respondent:
    <%include file="respondent.mako" args="task=task"/>
%endif

## ============================================================================
## Main task content
## ============================================================================

${ task.get_task_html(req) | n }

## ============================================================================
## "Office" stuff
## ============================================================================

<div class="office">
    ${ _("Created on device at:") }
        ${ format_datetime(task.when_created, DateFormat.SHORT_DATETIME_SECONDS) }.
    ${ _("Last modified at:") }
        ${ format_datetime(task.when_last_modified, DateFormat.SHORT_DATETIME_SECONDS) }.
    ${ _("Table:") }
        ${ task.tablename }.
    ${ _("Task PK on client device:") }
        ${ task.id }.
    ${ _("Uploading device ID:") }
        ${ task._device.get_friendly_name_and_id() if task._device else "?" }.
    ${ _("Tablet CamCOPS version at upload:") }
        ${ task._camcops_version }.
    ${ _("Uploaded at:") }
        ${ format_datetime(task._when_added_exact, DateFormat.SHORT_DATETIME_SECONDS) }.
    ${ _("Group:") }
        ${ task._group.name } (${ task._group_id }).
    ${ _("Added by:") }
        ${ task.get_adding_user_username() }.
    ${ _("Server PK:") }
        ${ task.pk }
        (${ _("predecessor") } ${ task._predecessor_pk },
        ${ _("successor") } ${ task._successor_pk }).
    ${ _("Current?") }
        %if task._current:
            ## some repetition as harder to have no space before "." otherwise!
            ${ get_yes_no(req, True) }.
        %else:
            ${ get_yes_no(req, False) }
            %if task._successor_pk is None:
                (${ _("deleted") }
            %else:
                (${ _("modified") }
            %endif
            ## TRANSLATOR: ... deleted/modified... by <username>... at <time>
            ${ _("by") }
                ${ task.get_removing_user_username() }
            ## TRANSLATOR: ... deleted/modified... by <username>... at <time>
            ${ _("at") }
                ${ format_datetime(task._when_removed_exact, DateFormat.SHORT_DATETIME_SECONDS) }.
        %endif
    ${ _("Preserved/erased from tablet?") }
        %if task.is_preserved():
            ${ get_yes_no(req, True) }
            %if task.was_forcibly_preserved():
                ## TRANSLATOR: ... [forcibly] preserved... by <username>... at <time>
                (${ _("forcibly preserved") }
            %else:
                ## TRANSLATOR: ... [forcibly] preserved... by <username>... at <time>
                (${ _("preserved") }
            %endif
            ## TRANSLATOR: ... [forcibly] preserved... by <username>... at <time>
            ${ _("by") }
                ${ task.get_preserving_user_username() }
            ## TRANSLATOR: ... [forcibly] preserved... by <username>... at <time>
            ${ _("at") }
                ${ task.era }.
            ## ... already an UTC ISO8601 string (BUT Python transformation now).
        %else:
            ${ get_yes_no(req, False) }.
        %endif
    ${ _("Patient server PK used:") }
        ${ task.get_patient_server_pk() if not task.is_anonymous else "N/A" }.
    ## TRANSLATOR: Information received from <url> (server version <version>) at: <datetime>.
    ${ _("Information retrieved from") }
        ${ req.url }
    ## TRANSLATOR: Information received from <url> (server version <version>) at: <datetime>.
    (${ _("server version") }
        ${ CAMCOPS_SERVER_VERSION_STRING })
    ## TRANSLATOR: Information received from <url> (server version <version>) at: <datetime>.
    ${ _("at:") }
        ${ format_datetime(req.now, DateFormat.SHORT_DATETIME_SECONDS) }.
</div>

## ============================================================================
## Extra hyperlinks for web version
## ============================================================================

%if viewtype == ViewArg.HTML:

    <div class="office">

        ## Link to help
        ${ req.icon_text(
            icon=Icons.INFO_EXTERNAL,
            url=task.help_url(),
            text=_("Task help")
        ) | n }
        |
        ## Link to details
        ${ req.icon_text(
            icon=Icons.INFO_INTERNAL,
            url=req.route_url(Routes.TASK_DETAILS, table_name=task.tablename),
            text=_("Task details")
        ) | n }


        ## Link to XML and FHIR versions (always identifiable)
        %if not anonymise:
            <p>
                View raw data:
                ${ req.icon_text(
                        icon=Icons.XML,
                        url=req.route_url(
                            Routes.TASK,
                            _query={
                                ViewParam.TABLE_NAME: task.tablename,
                                ViewParam.SERVER_PK: task.pk,
                                ViewParam.VIEWTYPE: ViewArg.XML,
                            }
                        ),
                        text="XML"
                ) | n }
                |
                ${ req.icon_text(
                        icon=Icons.JSON,
                        url=req.route_url(
                            Routes.TASK,
                            _query={
                                ViewParam.TABLE_NAME: task.tablename,
                                ViewParam.SERVER_PK: task.pk,
                                ViewParam.VIEWTYPE: ViewArg.FHIRJSON,
                            }
                        ),
                        text="FHIR"
                ) | n }
            </p>
        %endif

        ## Link to anonymous version (or back to identifiable):
        <p>
            %if anonymise:
                ${ req.icon_text(
                    icon=Icons.HTML_IDENTIFIABLE,
                    url=req.route_url(
                        Routes.TASK,
                        _query={
                                ViewParam.TABLE_NAME: task.tablename,
                                ViewParam.SERVER_PK: task.pk,
                            ViewParam.VIEWTYPE: ViewArg.HTML,
                        }
                    ),
                    text=_("View identifiable version")
                ) | n }
            %else:
                View anonymised version:
                ${ req.icon_text(
                        icon=Icons.HTML_ANONYMOUS,
                        url=req.route_url(
                            Routes.TASK,
                            _query={
                                ViewParam.TABLE_NAME: task.tablename,
                                ViewParam.SERVER_PK: task.pk,
                                ViewParam.VIEWTYPE: ViewArg.HTML,
                                ViewParam.ANONYMISE: True,
                            }
                        ),
                        text="HTML"
                ) | n }
                |
                ${ req.icon_text(
                    icon=Icons.PDF_ANONYMOUS,
                    url=request.route_url(
                        Routes.TASK,
                        _query={
                            ViewParam.TABLE_NAME: task.tablename,
                            ViewParam.SERVER_PK: task.pk,
                            ViewParam.VIEWTYPE: ViewArg.PDF,
                            ViewParam.ANONYMISE: True,
                        }
                    ),
                    text="PDF"
                ) | n }
            %endif
        </p>
    </div>

    ## Superuser options
    %if not anonymise:
        <div class="superuser">
            ## check this collapses to zero height with no content!
            %if req.user.authorized_to_add_special_note(task._group_id):
                <p>
                    ${ req.icon_text(
                        icon=Icons.SPECIAL_NOTE,
                        url=request.route_url(
                            Routes.ADD_SPECIAL_NOTE,
                            _query={
                                ViewParam.TABLE_NAME: task.tablename,
                                ViewParam.SERVER_PK: task.pk,
                            }
                        ),
                        text=_("Add special note")
                    ) | n }
                </p>
            %endif
            %if req.user.may_administer_group(task._group_id):
                %if task.has_patient and task.patient and task.patient.is_finalized:
                    <p>
                        ${ req.icon_text(
                            icon=Icons.PATIENT_EDIT,
                            url=request.route_url(
                                Routes.EDIT_FINALIZED_PATIENT,
                                _query={
                                    ViewParam.SERVER_PK: task.patient.pk,
                                    ViewParam.BACK_TASK_TABLENAME: task.tablename,
                                    ViewParam.BACK_TASK_SERVER_PK: task.pk,
                                }
                            ),
                            text=_("Edit patient details")
                        ) | n }
                    </p>
                %endif
            %endif
            %if req.user.authorized_to_erase_tasks(task._group_id):
                ## Note: prohibit manual erasure for non-finalized tasks.
                %if task.era != ERA_NOW:
                    <p>
                    %if not task.is_erased():
                        ${ req.icon_text(
                            icon=Icons.DELETE_MAJOR,
                            url=request.route_url(
                                Routes.ERASE_TASK_LEAVING_PLACEHOLDER,
                                _query={
                                    ViewParam.TABLE_NAME: task.tablename,
                                    ViewParam.SERVER_PK: task.pk,
                                }
                            ),
                            text=_("Erase task instance, leaving placeholder")
                        ) | n }
                        |
                    %endif
                        ${ req.icon_text(
                            icon=Icons.DELETE_MAJOR,
                            url=request.route_url(
                                Routes.ERASE_TASK_ENTIRELY,
                                _query={
                                    ViewParam.TABLE_NAME: task.tablename,
                                    ViewParam.SERVER_PK: task.pk,
                                }
                            ),
                            text=_("Erase task entirely")
                        ) | n }
                    </p>
                %endif
            %endif
        </div>
    %endif

    ## Links to predecessor / successor / PDF

    <div class="navigation">
        ## Links to predecessor/successor
        %if task._predecessor_pk is not None:
            <p><i>
                An older version of this record exists:
                ${ req.icon_text(
                    icon=Icons.GOTO_PREDECESSOR,
                    url=request.route_url(
                        Routes.TASK,
                        _query={
                            ViewParam.TABLE_NAME: task.tablename,
                            ViewParam.SERVER_PK: task._predecessor_pk,
                            ViewParam.VIEWTYPE: ViewArg.HTML,
                        }
                    ),
                    text=_("view previous version")
                ) | n }
            </i></p>
        %endif
        %if task._successor_pk is not None:
            <p><b>
                An newer version of this record exists:
                ${ req.icon_text(
                    icon=Icons.GOTO_SUCCESSOR,
                    url=request.route_url(
                        Routes.TASK,
                        _query={
                            ViewParam.TABLE_NAME: task.tablename,
                            ViewParam.SERVER_PK: task._successor_pk,
                            ViewParam.VIEWTYPE: ViewArg.HTML,
                        }
                    ),
                    text=_("view next version")
                ) | n }
            </b></p>
        %endif

        ## Link to PDF version
        <p>
            %if anonymise:
                ${ req.icon_text(
                    icon=Icons.PDF_ANONYMOUS,
                    url=request.route_url(
                        Routes.TASK,
                        _query={
                            ViewParam.TABLE_NAME: task.tablename,
                            ViewParam.SERVER_PK: task.pk,
                            ViewParam.VIEWTYPE: ViewArg.PDF,
                            ViewParam.ANONYMISE: True,
                        }
                    ),
                    text=_("View anonymised PDF")
                ) | n }
            %else:
                ${ req.icon_text(
                    icon=Icons.PDF_IDENTIFIABLE,
                    url=request.route_url(
                        Routes.TASK,
                        _query={
                            ViewParam.TABLE_NAME: task.tablename,
                            ViewParam.SERVER_PK: task.pk,
                            ViewParam.VIEWTYPE: ViewArg.PDF,
                        }
                    ),
                    text=_("View PDF for printing/saving")
                ) | n }
            %endif
        </p>
    </div>

%endif

## ============================================================================
## Signature block for PDF version
## ============================================================================

%if signature:
    <%include file="clinician_signature_block.mako"/>
%endif
