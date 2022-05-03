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

INSTRUCTOR_TITLES = [
    ('Assistant Professor','Assistant Professor'),
    ('Associate Professor','Associate Professor'),
    ('Professor','Professor')
]

class UserLoginForm(forms.Form):
    username=forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Username'}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    usertype=forms.CharField(label='Type Of User',widget=forms.Select(choices=USER_TYPES))

class UserCreateForm(forms.Form):
    usertype=forms.CharField(label='Type Of User',widget=forms.Select(choices=USER_TYPES_CREATE))
    username=forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Username'}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    title=forms.CharField(label='Title Of Instructor',widget=forms.Select(choices=INSTRUCTOR_TITLES))
    name=forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Name'}))
    surname=forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Surname'}))
    email=forms.EmailField(label='Email')
    departmentID = forms.IntegerField(label='Department ID Number')

class DeleteStudent(forms.Form):
    studentID = forms.IntegerField(label='Student ID')

class UpdateTitle(forms.Form):
    username=forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Username'}))
    title=forms.CharField(label='Title Of Instructor',widget=forms.Select(choices=INSTRUCTOR_TITLES))

class GetStudentGrade(forms.Form):
    studentID = forms.IntegerField(label='Student ID')

class GetCourses(forms.Form):
    username=forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Instructor Username'}))

class GetAverageGrade(forms.Form):
    courseID = forms.IntegerField(label='Course ID')

class AddCourse(forms.Form):
    courseID = forms.IntegerField(label='Course ID')
