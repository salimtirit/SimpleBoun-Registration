from cmath import pi
from unittest import result
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from .forms import *
from .db_utils import run_statement
from hashlib import sha256


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
    password = sha256(password.encode("utf-8")).hexdigest()

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
        
    elif usertype == "student":    
        result=run_statement(f"SELECT * FROM {usertype.strip()} WHERE username='{username}';") #Run the query in DB
        isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False
        getSearchCourse = GetSearchCourse()
        addCourse=AddCourse()
        filterCourse = FilterCourse()
        return render(
            req,
            "studentHome.html",
            {
                "results":result,
                "username":username,
                "action_fail": isFailed,
                "add_course":addCourse,
                "get_search_course":getSearchCourse,
                "filtered_courses":filterCourse
            }
        )
    else:    
        getListClassroom=GetListClassroom()
        getListStudents=GetListStudents()
        createCourse = CreateCourse()
        updateCourseName = UpdateCourseName()
        giveGrade = GiveGrade()
        addPrerequisite = AddPrerequisite()
        viewCourses = run_statement(f"SELECT course.courseID, course.name, course.classroomID, time_slot, quota, GROUP_CONCAT(prerequisite) FROM simpleboundb.course LEFT JOIN simpleboundb.prerequisite_of ON prerequisite_of.subsequent = course.courseID LEFT JOIN simpleboundb.lectured_in ON lectured_in.courseID = course.courseID WHERE instructor_username = '{username}' GROUP BY course.courseID;")
        isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False
        return render(
            req,'instructorHome.html',
            {
                "get_list_classroom":getListClassroom,
                "get_list_students":getListStudents,
                "update_course_name":updateCourseName,
                "add_prerequisite":addPrerequisite,
                "username":username,
                "create_course":createCourse,
                "view_courses":viewCourses,
                "give_grade":giveGrade,
                "action_fail":isFailed,
            }
        )
 
def createUser(req):
    #Retrieve data from the request body
    usertype=req.POST["usertype"]
    username=req.POST["username"]
    password=req.POST["password"]
    password = sha256(password.encode("utf-8")).hexdigest()
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
        req.session["username"] = username
        return HttpResponseRedirect("../forum/instructorsCourses")
    else:
        return HttpResponseRedirect('../forum/home?fail=true')

def instructorsCourses(req):
    username = req.session["username"]
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

def getListClassroom(req):
    slot = req.POST["slot"]
    slot = slot[0][0]
    result=run_statement(f"SELECT * FROM lectured_in WHERE time_slot={slot};")
    if result:
        req.session["slot"] = slot
        return HttpResponseRedirect("../forum/listClassroom")
    else:
        return HttpResponseRedirect('../forum/home?fail=true')
    
    
def listClassroom(req):
    slot = req.session["slot"]
    result = run_statement(f"SELECT classroom.classroomID, campus, capacity FROM simpleboundb.lectured_in INNER JOIN classroom ON classroom.classroomID = lectured_in.classroomID WHERE time_slot={slot};")
    isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False

    return render(req,'listClassroom.html',{"result":result,"action_fail":isFailed,"slot":slot})

def getListStudents(req):
    course_id = req.POST["course_id"]
    result=run_statement(f"SELECT * FROM course WHERE courseID='{course_id}';")
    if result:
        req.session["course_id"] = course_id
        return HttpResponseRedirect("../forum/listStudents")
    else:
        return HttpResponseRedirect('../forum/home?fail=true')
    
    
def listStudents(req):
    course_id = req.session["course_id"]
    result = run_statement(f"SELECT username, student.studentID, email, name, surname FROM simpleboundb.enrolled INNER JOIN student ON student.studentID = enrolled.studentID WHERE courseID ='{course_id}';")
    isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False

    return render(req,'listStudents.html',{"result":result,"action_fail":isFailed,"course_id":course_id})

def createCourse(req):
    #Retrieve data from the request body
    username = req.session["username"] 
    courseID=req.POST["courseID"]
    course_name=req.POST["course_name"]
    credit=req.POST["credit"]
    classID=req.POST["classID"]
    slot=req.POST["slot"]
    quota=req.POST["quota"]
    
    department_ID = run_statement(f"SELECT departmentID FROM simpleboundb.instructor WHERE username='{username}';")
    departmentID = department_ID[0][0]

    try:
        run_statement(f"CALL CreateCourse({courseID},'{course_name}',{departmentID},{credit},'{username}',{classID},{quota});")
        run_statement(f"INSERT INTO lectured_in (`courseID`, `classroomID`, `time_slot`) VALUES ({courseID}, {classID}, {slot});")
        return HttpResponseRedirect("../forum/home")
    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../forum/home?fail=true')
    
def updateCourseName (req):
    courseID=req.POST["courseID"]
    course_name=req.POST["course_name"]

    try:
        run_statement(f"UPDATE course SET name = '{course_name}' WHERE courseID = '{courseID}';")
        return HttpResponseRedirect("../forum/home")
    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../forum/home?fail=true')

def giveGrade (req):
    courseID=req.POST["courseID"]
    studentID=req.POST["studentID"]
    grade=req.POST["grade"]
    username = req.session['username']
    
    is_enrolled = run_statement(f"SELECT * FROM enrolled where courseID = '{courseID}' AND studentID = '{studentID}';")
    course_given = run_statement(f"SELECT * FROM course where courseID = '{courseID}' AND instructor_username= '{username}';")
    if is_enrolled and course_given:
        try:
            run_statement(f"INSERT INTO grades (`studentID`, `courseID`, `grade`) VALUES ('{studentID}', '{courseID}', '{grade}');")
            run_statement(f"DELETE FROM enrolled WHERE studentID='{studentID}' AND courseID='{courseID}';")
            return HttpResponseRedirect("../forum/home")
        except Exception as e:
            print(str(e))
            return HttpResponseRedirect('../forum/home?fail=true')
    else:
        return HttpResponseRedirect('../forum/home?fail=true')
    
def addPrerequisite (req):

    courseID = req.POST["courseID"]
    pID = req.POST.get('pID', False)
    try:
        run_statement(f"INSERT INTO prerequisite_of (subsequent, prerequisite) VALUES ({courseID}, {pID});")
        return HttpResponseRedirect("../forum/home")
    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../forum/home?fail=true')


def getSearchCourse(req):
    keyword = req.POST["keyword"]
    result = run_statement(f"SELECT * FROM course WHERE course.name LIKE '%{keyword}%';")
    if result:
        req.session["keyword"] = keyword
        return HttpResponseRedirect("../forum/searchCourse")
    else:
        return HttpResponseRedirect('../forum/home?fail=true')
    
    
def searchCourse(req):
    keyword = req.session["keyword"]
    result = run_statement(f"SELECT course.courseID, course.name, instructor.surname, course.departmentID, credits, course.classroomID, time_slot, quota, GROUP_CONCAT(prerequisite) FROM simpleboundb.course INNER JOIN instructor ON instructor.username = instructor_username INNER JOIN simpleboundb.lectured_in ON lectured_in.courseID = course.courseID LEFT JOIN simpleboundb.prerequisite_of ON prerequisite_of.subsequent = course.courseID WHERE course.name LIKE '%{keyword}%' GROUP BY course.courseID;")
    isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False

    return render(req,'searchCourse.html',{"result":result,"action_fail":isFailed})

def listAllStudents(req):
    result=run_statement(f"SELECT username, name, surname, email, departmentID, completed_credits, GPA FROM student ORDER BY completed_credits ASC;") #Run the query in DB
    isFailed=req.GET.get("fail",False)
    return render(req,'allStudents.html',{"result":result,"action_fail":isFailed})
  
def listGivenCourses(req):
    #result = run_statement("select c.courseID, c.name, i.surname, d.name, c.credits, c.classroomID, l.time_slot, c.quota, p.prerequisite from course c inner join department d on c.departmentID = d.departmentID  inner join instructor i  on c.instructor_username = i.username inner join lectured_in l on c.courseID = l.courseID and c.classroomID left join prerequisite_of p on c.courseID = p.subsequent order by courseID;")
    result = run_statement("select c.courseID, c.name, i.surname, d.name, c.credits, c.classroomID, l.time_slot, c.quota,group_concat( p.prerequisite) from course c  inner join department d  on c.departmentID = d.departmentID  inner join instructor i  on c.instructor_username = i.username left join lectured_in l on c.courseID = l.courseID and c.classroomID left join prerequisite_of p on c.courseID = p.subsequent group by c.courseID order by c.courseID;")
    isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False
    return render(req,'allCourses.html',{"result":result,"action_fail":isFailed}) 

def listInstructors(req):
    result=run_statement(f"SELECT username, name, surname, email, departmentID, title FROM instructor;") #Run the query in DB
    isFailed=req.GET.get("fail",False)
    return render(req,'allInstructors.html',{"result":result,"action_fail":isFailed})

def listDBManagers(req):
    result=run_statement(f"SELECT username FROM databasemanager;") #Run the query in DB
    isFailed=req.GET.get("fail",False)
    return render(req,'allDBManagers.html',{"result":result,"action_fail":isFailed})


def addCourse(req):
    courseID = req.POST["courseID"]
    username = req.session["username"]
    result=run_statement(f"select count(*) from grades g where g.courseID={courseID} and g.studentID = (select studentID from student where name='{username}');") #Run the query in DB
    result1 = run_statement(f"select count(*) from prerequisite_of where subsequent={courseID} and prerequisite not in (select courseID from grades where studentID=(select studentID from student where name='{username}'));")
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