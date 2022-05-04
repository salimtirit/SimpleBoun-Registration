from cmath import pi
from unittest import result
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
        isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False
        createuserform=UserCreateForm() #Use Django Form object to create a blank form for the HTML page
        deleteStudentForm=DeleteStudent()
        updateTitleForm=UpdateTitle()
        getStudentGrade = GetStudentGrade()
        getCourses = GetCourses()
        getAverageGrade = GetAverageGrade()
        return render(
            req,
            'dbManagerHome.html',
            {
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
    elif usertype == 'student':
        isFailed=req.GET.get("fail",False)
        addCourse=AddCourse()
        filterCourse = FilterCourse()
        return render(
            req,
            "studentHome.html",
            {
                "username":username,
                "action_fail": isFailed,
                "add_course":addCourse,
                "filtered_courses":filterCourse
            }
        )
    else:    
        result=run_statement(f"SELECT * FROM {usertype.strip()} WHERE username='{username}';") #Run the query in DB
        isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False
        return render(req,'userHome.html',{"results":result,"action_fail":isFailed,"username":username})

def listStudents(req):
    result=run_statement(f"SELECT username, name, surname, email, departmentID, completed_credits, GPA FROM student ORDER BY completed_credits ASC;") #Run the query in DB
    isFailed=req.GET.get("fail",False)
    return render(req,'allStudents.html',{"result":result,"action_fail":isFailed})

def listInstructors(req):
    result=run_statement(f"SELECT username, name, surname, email, departmentID, title FROM instructor;") #Run the query in DB
    isFailed=req.GET.get("fail",False)
    return render(req,'allInstructors.html',{"result":result,"action_fail":isFailed})

def listDBManagers(req):
    result=run_statement(f"SELECT username FROM databasemanager;") #Run the query in DB
    isFailed=req.GET.get("fail",False)
    return render(req,'allDBManagers.html',{"result":result,"action_fail":isFailed})

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

def listGivenCourses(req):
    #result = run_statement("select c.courseID, c.name, i.surname, d.name, c.credits, c.classroomID, l.time_slot, c.quota, p.prerequisite from course c inner join department d on c.departmentID = d.departmentID  inner join instructor i  on c.instructor_username = i.username inner join lectured_in l on c.courseID = l.courseID and c.classroomID left join prerequisite_of p on c.courseID = p.subsequent order by courseID;")
    result = run_statement("select c.courseID, c.name, i.surname, d.name, c.credits, c.classroomID, l.time_slot, c.quota,group_concat( p.prerequisite) from course c  inner join department d  on c.departmentID = d.departmentID  inner join instructor i  on c.instructor_username = i.username inner join lectured_in l on c.courseID = l.courseID and c.classroomID left join prerequisite_of p on c.courseID = p.subsequent group by c.courseID order by c.courseID;")
    isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False
    return render(req,'allCourses.html',{"result":result,"action_fail":isFailed})

def addCourse(req):
    courseID = req.POST["courseID"]
    username = req.session["username"]
    print(courseID)
    result=run_statement(f"select count(*) from grades g where g.courseID={courseID} and g.studentID = (select studentID from student where name='{username}');") #Run the query in DB
    result1 = run_statement(f"select count(*) from prerequisite_of where subsequent={courseID} and prerequisite not in (select courseID from grades where studentID=(select studentID from student where name='{username}'));")
    print(result[0][0])
    print(result1[0][0])
    if result[0][0] > 0 or result1[0][0] > 0:
        return HttpResponseRedirect('../forum/home?fail=true')
    else:
        try:
            run_statement(f"insert into enrolled values((select studentID from student where name='{username}'),'{courseID}');")
            return HttpResponseRedirect("../forum/home")
        except Exception as e:
            print(str(e))
            return HttpResponseRedirect('../forum/home?fail=true')

def takenCourses(req):
    username = req.session["username"]
    studentID=run_statement(f"select studentID from student where name='{username}'")
    studentID = studentID[0][0]
    result = run_statement(f"select c.courseId, c.name, grade from course c ,(select courseID, grade from grades where studentID={studentID} union all  select courseID, Null as col3 from enrolled where studentID={studentID}) as a where c.courseID = a.courseID;")
    isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False
    return render(req,'takenCourses.html',{"result":result,"action_fail":isFailed})

def getFilteredCourses(req):
    departmentID = req.POST["departmentID"]
    campus = req.POST["campus"]
    minCredits = req.POST["minCredits"]
    maxCredits = req.POST["maxCredits"]

    result1 = False
    result2 = False
    if len(str(departmentID))>0:
        result1=run_statement(f"SELECT * FROM department WHERE departmentID={departmentID};") #Run the query in DB
    
    if len(str(campus))>0:
        result2=run_statement(f"SELECT * FROM classroom WHERE campus='{campus}';") #Run the query in DB
    
    if result1 and result2 and len(str(minCredits))>0 and len(str(maxCredits))>0 and maxCredits>minCredits:
        req.session["departmentID"] = departmentID
        req.session["campus"] = campus
        req.session["minCredits"] = minCredits
        req.session["maxCredits"] = maxCredits
        return HttpResponseRedirect("../forum/filteredCourses")
    else:
        return HttpResponseRedirect('../forum/home?fail=true')

def filteredCourses(req):
    departmentID = req.session["departmentID"]
    campus = req.session["campus"]
    minCredits = req.session["minCredits"]
    maxCredits = req.session["maxCredits"]

    result=run_statement(f"CALL FilterCourses({departmentID},'{campus}',{minCredits},{maxCredits});") #Run the query in DB
    isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False

    return render(req,'filteredCourses.html',{"result":result,"action_fail":isFailed})
