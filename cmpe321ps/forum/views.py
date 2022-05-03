from cmath import pi
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from .forms import *
from .db_utils import run_statement


def index(req):
    #Logout the user if logged 
    if req.session:
        req.session.flush()
    
    isFailed=req.GET.get("fail",False) #Check the value of the GET parameter "fail"
    
    loginForm=UserLoginForm() #Use Django Form object to create a blank form for the HTML page

    return render(req,'loginIndex.html',{"login_form":loginForm,"action_fail":isFailed})


def login(req):
    #Retrieve data from the request body
    username=req.POST["username"]
    password=req.POST["password"]
    usertype=req.POST["usertype"]

    result=run_statement(f"SELECT * FROM {usertype} WHERE username='{username}' and password='{password}';") #Run the query in DB

    if result: #If a result is retrieved
        req.session["username"]=username #Record username into the current session
        req.session["usertype"]=usertype
        return HttpResponseRedirect('../forum/home') #Redirect user to home page
    else:
        return HttpResponseRedirect('../forum?fail=true')


def homePage(req):
    usertype = req.session["usertype"]
    username = req.session["username"] #Retrieve the username of the logged-in user
    if usertype == "databasemanager":
        result_student=run_statement(f"SELECT username, name, surname, email, departmentID, completed_credits, GPA FROM student ORDER BY completed_credits ASC;") #Run the query in DB
        result_instructor=run_statement(f"SELECT username, name, surname, email, departmentID, title FROM instructor;") #Run the query in DB
        result_database_manager=run_statement(f"SELECT username FROM databasemanager;") #Run the query in DB
        isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False
        createuserform=UserCreateForm() #Use Django Form object to create a blank form for the HTML page
        deleteStudentForm=DeleteStudent()
        updateTitleForm=UpdateTitle()
        getStudentGrade = GetStudentGrade()
        getCourses = GetCourses()
        getAverageGrade = GetAverageGrade()
        return render(
            req,'dbManagerHome.html',
            {
                "result_student":result_student,
                "result_instructor":result_instructor,
                "result_database_manager":result_database_manager,
                "action_fail":isFailed,
                "username":username,
                "create_user":createuserform,
                'delete_student':deleteStudentForm,
                'update_title':updateTitleForm,
                'student_grades':getStudentGrade,
                'get_courses':getCourses,
                'average_grade':getAverageGrade
            }
        )
    else:    
        result=run_statement(f"SELECT * FROM {usertype.strip()} WHERE username='{username}';") #Run the query in DB
        isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False
        return render(req,'userHome.html',{"results":result,"action_fail":isFailed,"username":username})

def createUser(req):
    #Retrieve data from the request body
    usertype=req.POST["usertype"]
    username=req.POST["username"]
    password=req.POST["password"]
    name=req.POST["name"]
    surname=req.POST["surname"]
    email=req.POST["email"]
    departmentID=req.POST["departmentID"]
    title=req.POST["title"]

    if usertype == 'student':
        try:
            run_statement(f"CALL CreateStudent('{username}','{password}','{name}','{surname}','{email}',{departmentID});")
            return HttpResponseRedirect("../forum/home")
        except Exception as e:
            print(str(e))
            return HttpResponseRedirect('../forum/home?fail=true')
    elif usertype == 'instructor':
        try:
            run_statement(f"CALL CreateInstructor('{username}','{title}','{password}','{name}','{surname}','{email}',{departmentID});")
            return HttpResponseRedirect("../forum/home")
        except Exception as e:
            print(str(e))
            return HttpResponseRedirect('../forum/home?fail=true')


def deleteStudent(req):
    studentID = req.POST["studentID"]
    print(studentID)
    run_statement(f"DELETE FROM Student WHERE studentID = {studentID};")
    try:
        return HttpResponseRedirect("../forum/home")
    except Exception as e:
        print(str(e))
        return HttpResponseRedirect("../forum/home?fail=true")

def updateTitle(req):
    username = req.POST["username"]
    title=req.POST["title"]

    try:
        run_statement(f"UPDATE Instructor SET title ='{title}' WHERE username = '{username}';")
        return HttpResponseRedirect("../forum/home")
    except Exception as e:
        print(str(e))
        return HttpResponseRedirect("../forum/home?fail=true")

def getStudentGrades(req):
    studentID = req.POST["studentID"]
    print(studentID)
    result=run_statement(f"SELECT * FROM student WHERE studentID={studentID};") #Run the query in DB

    if result:
        req.session["grade_studentID"] = studentID
        return HttpResponseRedirect("../forum/studentGrades")
    else:
        return HttpResponseRedirect('../forum/home?fail=true')

def studentGrades(req):
    grade_studentID = req.session["grade_studentID"]
    result = run_statement(f"select c.courseID, name, grade from course c, grades g where g.studentID = {grade_studentID} and c.courseID = g.courseID;")
    isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False

    return render(req,'studentGrades.html',{"result":result,"action_fail":isFailed,"studentID":grade_studentID})

def getInstructorsCourses(req):
    username = req.POST["username"]
    print(username)
    result=run_statement(f"SELECT * FROM instructor WHERE username='{username}';") #Run the query in DB

    if result:
        req.session["class_instructor"] = username
        return HttpResponseRedirect("../forum/instructorsCourses")
    else:
        return HttpResponseRedirect('../forum/home?fail=true')

def instructorsCourses(req):
    username = req.session["class_instructor"]
    result = run_statement(f"select c.courseID, c.name, r.classroomID, campus, time_slot  from course c, classroom r, lectured_in l where c.instructor_username='{username}' and c.courseID = l.courseID and r.classroomID = l.classroomID;") #Run the query in DB
    isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False

    return render(req,'instructorsCourses.html',{"result":result,"action_fail":isFailed,"course_instructor":username})

def getAverageGrade(req):
    courseID = req.POST["courseID"]
    print(courseID)
    result=run_statement(f"SELECT * FROM course WHERE courseID='{courseID}';") #Run the query in DB
    
    if result:
        req.session["average_courseID"] = courseID
        return HttpResponseRedirect("../forum/averageGrade")
    else:
        return HttpResponseRedirect('../forum/home?fail=true')

def averageGrade(req):
    average_courseID = req.session["average_courseID"]
    result = run_statement(f"select g.courseID, c.name, AVG(g.grade) from course c, grades g where g.courseID ={average_courseID} and g.courseID=c.courseID;") #Run the query in DB
    isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False

    return render(req,'averageGrade.html',{"result":result,"action_fail":isFailed,"course_id":average_courseID})
