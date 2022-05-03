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
        result_student=run_statement(f"SELECT studentID, GPA, completed_credits, username, name, surname, email, departmentID FROM student;") #Run the query in DB
        result_instructor=run_statement(f"SELECT username, title, name, surname, email, departmentID FROM instructor;") #Run the query in DB
        result_database_manager=run_statement(f"SELECT username FROM databasemanager;") #Run the query in DB
        isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False
        createuserform=UserCreateForm() #Use Django Form object to create a blank form for the HTML page
        deleteStudentForm=DeleteStudent()
        return render(req,'dbManagerHome.html',{"result_student":result_student,"result_instructor":result_instructor,"result_database_manager":result_database_manager,"action_fail":isFailed,"username":username, "create_user":createuserform,'delete_student':deleteStudentForm})
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
            run_statement(f"CALL CreateStudent('{username}','{password}','{name}','{surname}','{email}',{departmentID})")
            return HttpResponseRedirect("../forum/home")
        except Exception as e:
            print(str(e))
            return HttpResponseRedirect('../forum/home?fail=true')
    elif usertype == 'instructor':
        try:
            run_statement(f"CALL CreateInstructor('{username}','{title}','{password}','{name}','{surname}','{email}',{departmentID})")
            return HttpResponseRedirect("../forum/home")
        except Exception as e:
            print(str(e))
            return HttpResponseRedirect('../forum/home?fail=true')

def deleteStudent(req):
    studentID = req.POST["studentID"]

    print(studentID)