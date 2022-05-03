from logging import PlaceHolder
from django import forms

USER_TYPES = [
    ('student','Student'),
    ('instructor','Instructor'),
    ('databasemanager','Database Manager')
]

USER_TYPES_CREATE = [
    ('student','Student'),
    ('instructor','Instructor')
]


class UserLoginForm(forms.Form):
    username=forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Username'}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    usertype=forms.CharField(label='Type Of User',widget=forms.Select(choices=USER_TYPES))

class UserCreateForm(forms.Form):
    usertype=forms.CharField(label='Type Of User',widget=forms.Select(choices=USER_TYPES_CREATE))
    username=forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Username'}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    #TODO make title dropdown
    title=forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Title (Only For Instructors)'})) 
    name=forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Name'}))
    surname=forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Surname'}))
    email=forms.EmailField(label='Email')
    departmentID = forms.IntegerField(label='Department ID Number')

# class DeleteStudent(forms.Form):
#     studentID = forms.IntegerField(label='Student ID')