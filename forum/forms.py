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


class GetListClassroom(forms.Form):
    slot = forms.IntegerField(label='Get Classroom List',widget=forms.TextInput(attrs={'placeholder':'Slot Number'}))
    
    
class GetListStudents(forms.Form):
    course_id = forms.IntegerField(label='Get Student List',widget=forms.TextInput(attrs={'placeholder':'Course ID'}))
    
class CreateCourse(forms.Form):
    courseID=forms.CharField(label='Create Course',widget=forms.TextInput(attrs={'placeholder':'Course ID'}))
    course_name=forms.CharField(label='',widget=forms.TextInput(attrs={'placeholder':'Course Name'}))
    credit=forms.CharField(label='',widget=forms.TextInput(attrs={'placeholder':'Credits'}))
    classID=forms.CharField(label='',widget=forms.TextInput(attrs={'placeholder':'Class ID'}))
    slot=forms.CharField(label='',widget=forms.TextInput(attrs={'placeholder':'Slot'}))
    quota = forms.IntegerField(label='',widget=forms.TextInput(attrs={'placeholder':'Quota'}))
    
class UpdateCourseName(forms.Form):
    courseID = forms.IntegerField(label='Update Course Name',widget=forms.TextInput(attrs={'placeholder':'Course ID'}))
    course_name = forms.CharField(label='',widget=forms.TextInput(attrs={'placeholder':'New Course Name'}))
    
class GiveGrade(forms.Form):
    courseID = forms.IntegerField(label='Give Grade',widget=forms.TextInput(attrs={'placeholder':'Course ID'}))
    studentID = forms.IntegerField(label='',widget=forms.TextInput(attrs={'placeholder':'Student ID'}))
    grade = forms.IntegerField(label='',widget=forms.TextInput(attrs={'placeholder':'Grade'}))

class AddPrerequisite (forms.Form):
    courseID = forms.IntegerField(label='Add Prerequisite',widget=forms.TextInput(attrs={'placeholder':'Course ID'}))
    pID = forms.IntegerField(label='',widget=forms.TextInput(attrs={'placeholder':'Prerequisite ID'}))


    


    