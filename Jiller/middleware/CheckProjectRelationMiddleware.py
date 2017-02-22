import json
import waffle
from django.http import Http404

from django.http import HttpResponseForbidden
from django.urls import resolve
from project.models import ProjectTeam, Issue
from re import compile

PROJECT_URLS = [compile(r'^project/.+')]
ISSUE_ORDER = compile(r'^project/issue_order/$')


class CheckProjectRelation(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def is_user_attached_to_project(self, user_id, project_id):
        project_team = ProjectTeam.objects.filter(project_id=project_id)
        if not project_team:
            raise Http404()
        for team in project_team:
            try:
                ProjectTeam.objects.get(
                    pk=team.id, employees=user_id)
            except ProjectTeam.DoesNotExist:
                continue
            else:
                return True
        return False

    def __call__(self, request):
        path = request.path_info.lstrip('/')
        if request.user.is_staff or \
                not any(m.match(path) for m in PROJECT_URLS):
            response = self.get_response(request)
            return response

        if waffle.flag_is_active(request, 'create_team') and path == 'project/create/':
            return self.get_response(request)

        resolved = resolve(request.path)
        if resolved.kwargs.get('project_id', False):
            if self.is_user_attached_to_project(request.user.id,
                                                resolved.kwargs['project_id']):
                response = self.get_response(request)
                return response

        if request.method == 'POST':
            response = self.get_response(request)
            return response

        return HttpResponseForbidden()
