from __future__ import unicode_literals

from datetime import datetime

from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.contrib.auth.models import Group
from sorl.thumbnail.shortcuts import get_thumbnail
from django.db.models.signals import m2m_changed, pre_save
from django.dispatch import receiver


class ProjectModelManager(models.Manager):
    def get_user_projects(self, user):
        user_projects = super(ProjectModelManager, self).get_queryset().filter(
            is_active=True)
        if user.is_superuser:
            return user_projects
        else:
            return user_projects.filter(
                projectteam__employees__id__exact=user.id)


@python_2_unicode_compatible
class Project(models.Model):
    title = models.CharField(verbose_name=_('Title'), max_length=255)
    description = models.TextField(verbose_name=_('Description'), null=True,
                                   blank=True)
    start_date = models.DateField(verbose_name=_('Start date'),
                                  default=timezone.now)
    end_date = models.DateField(verbose_name=_('End date'), null=True,
                                blank=True)
    is_active = models.BooleanField(verbose_name=_('Is active'), null=False,
                                    default=True)

    def __str__(self):
        return self.title

    objects = ProjectModelManager()


@python_2_unicode_compatible
class Sprint(models.Model):
    NEW = 'new'
    ACTIVE = 'active'
    FINISHED = 'finished'
    SPRINT_STATUS_CHOICES = (
        (NEW, _('New')),
        (ACTIVE, _('Active')),
        (FINISHED, _('Finished'))
    )
    title = models.CharField(verbose_name=_('Title'), max_length=255)
    project = models.ForeignKey(Project, verbose_name=_('Project'))
    start_date = models.DateField(verbose_name=_('Start date'), null=True,
                                  blank=True)
    end_date = models.DateField(verbose_name=_('End date'), null=True,
                                blank=True)
    order = models.PositiveIntegerField(verbose_name=_('Order'), null=True,
                                        blank=True)
    status = models.CharField(verbose_name=_('Status'),
                              choices=SPRINT_STATUS_CHOICES, default=NEW,
                              max_length=255)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):

        # disable 2 active sprints in project at time exclude self
        if self.status == Sprint.ACTIVE:
            if len(Sprint.objects.filter(
                    project_id=self.project, status=Sprint.ACTIVE)
                           .exclude(pk=self.id)) >= 1:
                raise ValidationError(
                    "Another active sprint already exists in this project")

        if not self.id:
            self.order = len(
                Sprint.objects.filter(project_id=self.project)) + 1

        if self.status not in (Sprint.ACTIVE, Sprint.NEW):
            sprint_unfinished_issues = Issue.objects.filter(
                sprint=self.id).exclude(
                status__in=(Issue.CLOSED, Issue.RESOLVED, Issue.DELETED))
            for issue in sprint_unfinished_issues:
                issue.sprint = None
                issue.status = Issue.NEW
                issue.order = Issue.HIGH
                issue.save()

        super(Sprint, self).save(*args, **kwargs)


@python_2_unicode_compatible
class Issue(models.Model):
    NEW = 'new'
    IN_PROGRESS = 'in progress'
    RESOLVED = 'resolved'
    CLOSED = 'closed'
    DELETED = 'deleted'
    ISSUE_STATUS_CHOICES = (
        (NEW, _('New')),
        (IN_PROGRESS, _('In Progress')),
        (RESOLVED, _('Resolved')),
        (CLOSED, _('Closed')),
    )
    HIGH = -1
    MEDIUM = -2
    LOW = -3
    ISSUE_PRIORITY = (
        (HIGH, _('High')),
        (MEDIUM, _('Medium')),
        (LOW, _('Low'))
    )
    root = models.ForeignKey('self', null=True, blank=True)
    project = models.ForeignKey(Project, verbose_name=_('Project'))
    sprint = models.ForeignKey(Sprint, verbose_name=_('Sprint'),
                               null=True, blank=True)
    author = models.ForeignKey('employee.Employee', verbose_name=_('Author'),
                               related_name='author_issue_set')
    employee = models.ForeignKey('employee.Employee',
                                 verbose_name=_('Employee'),
                                 related_name='employee_issue_set', null=True,
                                 blank=True)
    title = models.CharField(verbose_name=_('Title'), max_length=255)
    description = models.TextField(verbose_name=_('Description'), null=True,
                                   blank=True)
    status = models.CharField(verbose_name=_('Status'),
                              choices=ISSUE_STATUS_CHOICES, default=NEW,
                              max_length=255)
    estimation = models.PositiveIntegerField(verbose_name=_('Estimation'),
                                             validators=[
                                                 MaxValueValidator(240)],
                                             null=True, blank=True)
    order = models.PositiveIntegerField(verbose_name=_('Priority'), default=0,
                                        choices=ISSUE_PRIORITY)

    def calculate_issue_priority(self):
        if self.order == Issue.HIGH:
            self.order = 0
        elif self.order == Issue.MEDIUM:
            self.order = Issue.objects.filter(project=self.project). \
                             filter(sprint__isnull=True).count() / 2
        elif self.order == Issue.LOW:
            self.order = Issue.objects.filter(project=self.project). \
                filter(sprint__isnull=True).count()

    def __str__(self):
        return self.title

    def child(self):
        if self.issue_set.exists():
            return self.issue_set.all()
        return False

    def save(self, *args, **kwargs):
        self.calculate_issue_priority()
        if self.sprint and self.sprint.project != self.project:
            raise ValidationError("Sprint is incorrect")
        super(Issue, self).save(*args, **kwargs)


@python_2_unicode_compatible
class IssueComment(models.Model):
    text = models.CharField(max_length=255, verbose_name=_('Text'))
    issue = models.ForeignKey(Issue, verbose_name=_('Issue'))
    author = models.ForeignKey('employee.Employee', verbose_name=_('Author'))
    date_created = models.DateTimeField(default=timezone.now,
                                        verbose_name=_('Date created'))

    def __str__(self):
        return self.title

    def get_pretty_date_created(self):
        return datetime.strftime(self.date_created, "%d.%m.%y %H:%M")

    def get_cropped_photo(self, *args, **kwargs):
        return get_thumbnail(self.photo, '40x40', crop='center')

    class Meta:
        ordering = ['-date_created']


@python_2_unicode_compatible
class ProjectTeam(models.Model):
    project = models.ForeignKey(Project, verbose_name=_('Project'))
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    employees = models.ManyToManyField('employee.Employee',
                                       verbose_name=_('Employees'))

    def __str__(self):
        return self.title


# check ProjectTeam for Project Manager in it before save
def check_save_team_without_pm(action, **kwargs):
    from employee.models import Employee
    if action == 'post_add':
        print kwargs['pk_set']
        for user_id in kwargs['pk_set']:
            if Employee.objects.filter(pk=user_id)[0]:
                print user_id
                print Employee.objects.filter(pk=user_id)[0].groups.filter(name='project manager').exists()
               # print Employee.objects.get(pk=user_id).groups.get().id
        else:
            raise ValidationError(
                "ProjectTeam cannot be saved without Project Manager")
m2m_changed.connect(check_save_team_without_pm,
                    sender=ProjectTeam.employees.through)

# check for 2nd team before create new
@receiver(pre_save, sender=ProjectTeam)
def delete_user_without_team(instance, **kwargs):
    team_in_project = ProjectTeam.objects.filter(project=instance.project_id)

    if len (team_in_project) > 1 or (len (team_in_project) == 1
                                     and instance not in team_in_project):
        raise ValidationError(
            "There is already another team in the project!")


@python_2_unicode_compatible
class ProjectNote(models.Model):
    project = models.ForeignKey(Project, verbose_name=_('Project'))
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    content = models.TextField(verbose_name=_('Note text'), null=True,
                               blank=True)

    def __str__(self):
        return self.title

