# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-24 21:32
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.ASCIIUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('role', models.CharField(choices=[('developer', 'Developer'), ('product owner', 'Product Owner'), ('scrum master', 'Scrum Master')], max_length=255, verbose_name='Role')),
                ('date_birth', models.DateField(blank=True, null=True, verbose_name='Date birth')),
                ('photo', models.ImageField(blank=True, null=True, upload_to='avatars/')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('status', models.CharField(blank=True, choices=[('new', 'New'), ('in progress', 'In Progress'), ('resolved', 'Resolved')], default='new', max_length=255, null=True, verbose_name='Status')),
                ('estimation', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(240)], verbose_name='Estimation')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='author_user', to=settings.AUTH_USER_MODEL, verbose_name='Author')),
                ('employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='worker_user', to=settings.AUTH_USER_MODEL, verbose_name='Employee')),
            ],
        ),
        migrations.CreateModel(
            name='IssueLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Time')),
                ('labor_costs', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(240)], verbose_name='Labor costs')),
                ('note', models.TextField(verbose_name='Note')),
                ('issue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workflow.Issue', verbose_name='Issue')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Employee')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('start_date', models.DateField(auto_now_add=True, verbose_name='Start date')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='End date')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectTeam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('employees', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Employees')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workflow.Project', verbose_name='Project')),
            ],
        ),
        migrations.CreateModel(
            name='Sprint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('start_date', models.DateField(blank=True, null=True, verbose_name='Start date')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='End date')),
                ('order', models.PositiveIntegerField(blank=True, null=True, verbose_name='Order')),
                ('status', models.CharField(blank=True, choices=[('new', 'New'), ('active', 'Active'), ('finished', 'Finished')], max_length=255, null=True, verbose_name='Status')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workflow.Project')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workflow.ProjectTeam')),
            ],
        ),
        migrations.AddField(
            model_name='issue',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='workflow.Project'),
        ),
        migrations.AddField(
            model_name='issue',
            name='root',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='workflow.Issue'),
        ),
        migrations.AddField(
            model_name='issue',
            name='sprint',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workflow.Sprint', verbose_name='Sprint'),
        ),
    ]