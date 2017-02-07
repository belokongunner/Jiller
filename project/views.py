import datetime

from django.db.models import Q
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView
from django.urls import reverse

from project.forms import IssueCommentCreateForm
from .forms import ProjectForm, SprintCreateForm, CreateIssueForm, \
    EditIssueForm, CreateTeamForm
from .models import Project, ProjectTeam, Issue, Sprint

from employee.models import Employee

from django.utils.decorators import method_decorator
from .decorators import delete_project, \
    edit_project_detail, create_project, create_sprint
from waffle.decorators import waffle_flag
from .tables import ProjectTable, SprintsListTable
from django_tables2 import SingleTableView, RequestConfig
import json
from employee.models import Employee
from employee.tables import ProjectTeamEmployeeTable, ProjectTeamEmployeeAddTable


class ProjectListView(SingleTableView):
    model = Project
    table_class = ProjectTable
    template_name = 'project/projects.html'
    table_pagination = True

    table_pagination = {
        'per_page': 10
    }

    def get_queryset(self):
        projects = Project.objects.get_user_projects(
            self.request.user).order_by(
            '-start_date')
        return projects


def sprints_list(request, project_id):
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        raise Http404("Project does not exist")
    sprints = Sprint.objects.filter(project=project_id) \
        .exclude(status=Sprint.ACTIVE)

    return render(request, 'project/sprints_list.html', {'project': project,
                                                         'sprints': sprints})


def backlog(request, project_id):
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        raise Http404("Project does not exist")
    issues = Issue.objects.filter(project=project_id) \
        .filter(sprint__isnull=True).filter(~Q(status = 'deleted'))

    return render(request, 'project/backlog.html', {'project': project,
                                                    'issues': issues})


@waffle_flag('create_issue', 'project:list')
def issue_create_view(request, project_id):
    if request.method == "POST":
        form = CreateIssueForm(request.POST)
        if form.is_valid():
            new_issue = form.save(commit=False)
            new_issue.save()
            return redirect('project:backlog', project_id)
    else:
        initial = {'project': project_id, 'author': request.user.id}
        if request.GET.get('root', False):
            initial['root'] = request.GET['root']
        form = CreateIssueForm(initial=initial)
    return render(request, 'project/issue_create.html', {'form': form,
                                                         'project': Project.objects.get(
                                                             pk=project_id)})


@waffle_flag('edit_issue', 'project:list')
def issue_edit_view(request, project_id, issue_id):
    current_issue = get_object_or_404(Issue, pk=issue_id, project=project_id)
    if request.method == "POST":
        form = EditIssueForm(request.POST, instance=current_issue)
        if form.is_valid():
            current_issue = form.save(commit=False)
            current_issue.save()
            return redirect('project:backlog', project_id)
    else:
        form = EditIssueForm(instance=current_issue)
    return render(request, 'project/issue_edit.html',
                  {'form': form, 'project': Project.objects.get(pk=project_id),
                   'issue': Issue.objects.get(pk=issue_id)})


def team_view(request, project_id):
    current_project = get_object_or_404(Project, pk=project_id)
    # hide PMs on "global" team board
    user_list = Employee.objects.filter(pm_role_access=False)

    try:
        team_list = ProjectTeam.objects.filter(project=current_project)
    except ProjectTeam.DoesNotExist:
        raise Http404("No team on project")

    return render(request, 'project/team.html', {'team_list': team_list,
                                                 'project': current_project,
                                                 'user_list': user_list})

# def team_view(request, project_id):
#     current_project = get_object_or_404(Project, pk=project_id)
#     # hide PMs on "global" team board
#     user_list = Employee.objects.filter(pm_role_access=False)
#     table_add = ProjectTeamEmployeeAddTable(user_list)
#     try:
#         teams_list = ProjectTeam.objects.filter(project=current_project)
#     except ProjectTeam.DoesNotExist:
#         raise Http404("No team on project")
#
#     employee_list = []
#     for team in teams_list:
#         if team.employees:
#             for employee in team.employees.all():
#                 employee_list.append(employee)
#
#     table_cur = ProjectTeamEmployeeTable(employee_list)
#     RequestConfig(request, paginate={'per_page': (9 - len(employee_list))}).configure(table_add)
#     return render(request, 'project/team.html', {'table_cur': table_cur,
#                                                  'table_add': table_add,
#                                                  'project': current_project,
#                                                  'team': teams_list})


def issue_detail_view(request, project_id, issue_id):
    current_issue = get_object_or_404(Issue, pk=issue_id)
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        form = IssueCommentCreateForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.issue = current_issue
            comment.save()
            return redirect(reverse('project:issue_detail', args=(project.id,
                                                                  current_issue.id)))

    if current_issue.project_id != project.id:
        raise Http404("Issue does not exist")
    context = {
        'issue': current_issue, 'project': project
    }
    if current_issue.root:
        context['root_issue'] = Issue.objects.get(pk=current_issue.root.id)
    child_issues = Issue.objects.filter(root=current_issue.id)
    if child_issues:
        context['child_issues'] = child_issues
    context['form'] = IssueCommentCreateForm()
    return render(request, 'project/issue_detail.html', context)


class IssueDeleteView(DeleteView):
    model = Issue
    query_pk_and_slug = True
    pk_url_kwarg = 'issue_id'

    def get_success_url(self):
        return reverse('project:backlog',
                       kwargs={'project_id': self.object.project_id})

    def get_context_data(self, **kwargs):
        context = super(IssueDeleteView, self).get_context_data(**kwargs)
        currrent_project = self.kwargs['project_id']
        current_issue = self.kwargs['issue_id']
        context['project'] = Project.objects.get(id=currrent_project)
        context['issue'] = Issue.objects.get(id=current_issue)
        return context

    def delete(self, request, *args, **kwargs):
        project = Project.objects.get(id=kwargs['project_id'])
        issue = Issue.objects.get(id=kwargs['issue_id'])
        issue.status = 'deleted';
        issue.save()
        return HttpResponseRedirect(reverse('project:backlog',
                                            kwargs={'project_id': project.id}))


class SprintView(DetailView):
    model = Sprint
    template_name = 'project/sprint_detail.html'
    query_pk_and_slug = True
    pk_url_kwarg = 'sprint_id'
    slug_field = 'project'
    slug_url_kwarg = 'project_id'

    def get_context_data(self, **kwargs):
        context = super(SprintView, self).get_context_data(**kwargs)
        cur_proj = self.kwargs['project_id']
        cur_spr = self.kwargs['sprint_id']
        issues_from_this_sprint = Issue.objects.filter(project_id=cur_proj,
                                                       sprint_id=cur_spr)
        context['new_issues'] = issues_from_this_sprint.filter(status="new")
        context['in_progress_issues'] = \
            issues_from_this_sprint.filter(status="in progress")
        context['resolved_issues'] = \
            issues_from_this_sprint.filter(status="resolved")
        context['closed_issues'] = issues_from_this_sprint.filter(
            status="closed")
        context['project'] = Project.objects.get(id=cur_proj)
        return context


class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    query_pk_and_slug = True
    pk_url_kwarg = 'project_id'
    template_name = 'project/project_create_form.html'

    def get_success_url(self):
        return reverse('project:detail',
                       kwargs={'project_id': self.object.id})

    @method_decorator(create_project)
    def dispatch(self, *args, **kwargs):
        return super(ProjectCreateView, self).dispatch(*args, **kwargs)


class ProjectDetailView(DetailView):
    model = Project
    query_pk_and_slug = True
    pk_url_kwarg = 'project_id'
    template_name = 'project/project_detail.html'


class ProjectUpdateView(UpdateView):
    model = Project
    form_class = ProjectForm
    query_pk_and_slug = True
    pk_url_kwarg = 'project_id'
    template_name = 'project/project_update_form.html'

    def get_success_url(self):
        return reverse('project:detail',
                       kwargs={'project_id': self.object.id})

    @method_decorator(edit_project_detail)
    def dispatch(self, *args, **kwargs):
        return super(ProjectUpdateView, self).dispatch(*args, **kwargs)


class ProjectDeleteView(DeleteView):
    model = Project
    query_pk_and_slug = True
    pk_url_kwarg = 'project_id'

    def get_success_url(self):
        return reverse('project:list')

    def delete(self, request, *args, **kwargs):
        project = Project.objects.get(id=kwargs['project_id'])

        project.is_active = False
        project.save()
        return HttpResponseRedirect(
            reverse('project:list'))

    @method_decorator(delete_project)
    def dispatch(self, *args, **kwargs):
        return super(ProjectDeleteView, self).dispatch(*args, **kwargs)


class SprintCreate(CreateView):
    model = Sprint
    form_class = SprintCreateForm
    query_pk_and_slug = True
    pk_url_kwarg = 'project_id'
    template_name_suffix = '_create_form'

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(SprintCreate, self).get_form_kwargs()
        kwargs.pop('instance', None)
        kwargs['project'] = self.project
        return kwargs

    def get_initial(self):
        return {'status': Sprint.NEW}

    def form_valid(self, form):
        sprint = form.save(commit=False)
        sprint.project = self.project
        sprint.start_date = datetime.datetime.now()
        sprint.save()
        issue = form.cleaned_data['issue']
        issue.update(sprint=sprint)
        self.object = sprint
        return redirect(
            reverse('project:sprint_active', args=(self.object.project.id,)))

    def get_context_data(self, **kwargs):
        project = Project.objects.get(id=self.kwargs['project_id'])
        context = super(SprintCreate, self).get_context_data(**kwargs)
        context['project'] = self.project
        context['issue_list'] = project.issue_set.filter(sprint=None)
        return context

    def get_success_url(self):
        return reverse('project:sprint_detail', args=(self.object.project.id,
                                                      self.object.id))

    @method_decorator(create_sprint)
    def dispatch(self, *args, **kwargs):
        self.project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        return super(SprintCreate, self).dispatch(*args, **kwargs)


class ActiveSprintView(DetailView):
    model = Sprint
    query_pk_and_slug = True
    pk_url_kwarg = 'project_id'
    template_name = 'project/sprint_active.html'

    def get_object(self, queryset=None):
        try:
            return super(ActiveSprintView, self).get_object(queryset)
        except:
            try:
                Project.objects.get(pk=self.kwargs['project_id'])
            except:
                raise Http404("Project does not exist")
        else:
            return None

    def get_context_data(self, **kwargs):
        context = super(ActiveSprintView, self).get_context_data(
            **kwargs)

        try:
            Sprint.objects.get(project_id=self.kwargs['project_id'],
                               status='active')
        except Sprint.DoesNotExist:
            context['project'] = Project.objects.get(
                id=self.kwargs['project_id'])
            context['no_active_sprint'] = True
            return context
        else:
            active_sprint = Sprint.objects.get(
                project_id=self.kwargs['project_id'],
                status='active')
            context['active_sprint'] = active_sprint
            issues_from_active_sprint = Issue.objects.filter(
                project_id=self.kwargs['project_id'],
                sprint_id=active_sprint.id)
            context['new_issues'] = issues_from_active_sprint.filter(
                status="new")
            context['in_progress_issues'] = issues_from_active_sprint.filter(
                status="in progress")
            context['resolved_issues'] = issues_from_active_sprint.filter(
                status="resolved")
            context['project'] = Project.objects.get(
                id=self.kwargs['project_id'])
            return context


@waffle_flag('push_issue', 'project:list')
def push_issue_in_active_sprint(request, project_id, issue_id, slug):
    current_issue = get_object_or_404(Issue, pk=issue_id)
    sprint = get_object_or_404(Sprint, pk=current_issue.sprint_id)

    if slug == 'right' and sprint.status == 'active':
        if current_issue.status == "new":
            current_issue.status = "in progress"
            current_issue.save()
        elif current_issue.status == "in progress":
            current_issue.status = "resolved"
            current_issue.save()
    elif slug == 'left' and sprint.status == 'active':
        if current_issue.status == "resolved":
            current_issue.status = "in progress"
            current_issue.save()
        elif current_issue.status == "in progress":
            current_issue.status = "new"
            current_issue.save()
    return HttpResponseRedirect(reverse('project:sprint_active',
                                        args=(project_id)))


class SprintStatusUpdate(UpdateView):
    model = Sprint
    template_name = 'project/sprint_update_form.html'
    pk_url_kwarg = 'sprint_id'
    slug_field = 'project'
    slug_url_kwarg = 'project_id'
    fields = ['status']

    def get_context_data(self, **kwargs):
        context = super(SprintStatusUpdate, self).get_context_data(**kwargs)
        context['project'] = Project.objects.get(id=self.kwargs['project_id'])
        return context

    def get_success_url(self, **kwargs):
        return reverse('project:sprint_active',
                       kwargs={'project_id': self.object.project_id})


@waffle_flag('prioritize_issue', 'project:detail')
def issue_order(request):
    if request.method == 'POST':
        data = json.loads(request.POST.get('data'))
        keys = data.keys()

        if data:
            for key in keys:
                try:
                    issue = Issue.objects.get(id=int(key))
                except Issue.DoesNotExist:
                    raise Http404("Issue does not exist")
                issue.order = int(data[key])
                issue.save()
        return HttpResponse()
    else:
        return HttpResponseRedirect(reverse('project:list'))


def change_user_in_team(request, project_id, user_id, team_id):
    if request.method == 'POST':
        user = Employee.objects.get(pk=user_id)
        if 'add' in request.POST:
            team = get_object_or_404(ProjectTeam, pk=team_id)
            team.employees.add(user)
        if 'remove' in request.POST:
            team = get_object_or_404(ProjectTeam, pk=team_id)
            team.employees.remove(user)
        return redirect('project:team', project_id)
    return redirect('project:team', project_id)


def team_create(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        form = CreateTeamForm(request.POST)
        if form.is_valid():
            new_team = form.save(commit=False)
            new_team.project = project
            new_team.save()
            new_team.employees.add(request.user.id)
            return redirect('project:team', project_id)
    else:
        form = CreateTeamForm()
    return render(request, 'project/team_create.html', {'form': form,
                                                        'project': project})


"""
class SprintDelete(DeleteView):
    model = Sprint

    def delete(self, **kwargs):
        sprint = Sprint.objects.get(id=self.kwargs['pk'])
        sprint.is_active = False
        sprint.save()
        return HttpResponseRedirect(
            reverse('project:sprints_list'))
"""
