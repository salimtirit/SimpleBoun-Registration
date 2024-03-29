from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home',views.homePage,name="homePage"),
    path('login',views.login,name="login"),
    path('createUser',views.createUser,name="createUser"),
    path('deleteStudent',views.deleteStudent,name="deleteStudent"),
    path('updateTitle',views.updateTitle,name="updateTitle"),
    path('getStudentGrades',views.getStudentGrades,name="getStudentGrades"),
    path('studentGrades',views.studentGrades,name="studentGrades"),
    path('getInstructorsCourses',views.getInstructorsCourses,name="getInstructorsCourses"),
    path('instructorsCourses',views.instructorsCourses,name="instructorsCourses"),
    path('getAverageGrade',views.getAverageGrade,name="getAverageGrade"),
    path('averageGrade',views.averageGrade,name="averageGrade"),
    path('allCourses',views.listGivenCourses,name="allCourses"),
    path('allStudents',views.listAllStudents,name="allStudents"),
    path('allInstructors',views.listInstructors,name="allInstructors"),
    path('allDBManagers',views.listDBManagers,name="allDBManagers"),
    path('addCourse',views.addCourse,name="addCourse"),
    path('takenCourses',views.takenCourses,name="takenCourses"),
    path('getFilteredCourses',views.getFilteredCourses,name="getFilteredCourses"),
    path('filteredCourses',views.filteredCourses,name="filteredCourses"),
    
    path('listClassroom',views.listClassroom,name="listClassroom"),
    path('getListClassroom',views.getListClassroom,name="getListClassroom"),
    path('listStudents',views.listStudents,name="listStudents"),
    path('getListStudents',views.getListStudents,name="getListStudents"),
    path('createCourse',views.createCourse,name="createCourse"),
    path('updateCourseName',views.updateCourseName,name="updateCourseName"),
    path('giveGrade',views.giveGrade,name="giveGrade"),
    path('addPrerequisite',views.addPrerequisite,name="addPrerequisite"),
    path('searchCourse',views.searchCourse,name="searchCourse"),
    path('getSearchCourse',views.getSearchCourse,name="getSearchCourse")

]