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
    path('addCourse',views.addCourse,name="addCourse")
]