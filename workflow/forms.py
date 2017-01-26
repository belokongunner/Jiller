from django import forms
from django.forms import ModelForm, Select, RadioSelect
from .models import Issue


class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=255)
    password = forms.CharField(label='Password', max_length=255)


class RegistrationForm(forms.Form):
    username = forms.CharField(label='Username', max_length=255)
    password = forms.CharField(label='Password', max_length=255)
    email = forms.CharField(label='Email', max_length=255)
    last_name = forms.CharField(label='Last name', max_length=255)
    first_name = forms.CharField(label='First name', max_length=255)


class EditIssueForm(ModelForm):
    class Meta:
        model = Issue
        fields = ('project', 'sprint', 'author', 'employee', 'title', 'description', 'status')
        widgets = {
            'status': RadioSelect(),
        }
