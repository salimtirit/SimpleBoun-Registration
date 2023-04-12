## Description ##
This is a course project, implementing a course registration database with a web-based user interface using the structure designed in a previous project. The database contains information about users, departments, courses, grades, and database managers. The system allows students, instructors, and database managers to log in, and users are able to perform operations that are defined for their roles.

The system allows database managers to add new users (students or instructors), delete students by providing the student ID, update the titles of the instructors by providing the instructor username and title, and view all students in ascending order of completed credits. Students can view their added courses for the current semester and add new courses if they meet the prerequisites. Instructors can view the courses they are teaching, and students enrolled in their courses. Additionally, instructors can submit grades for the courses they are teaching.

The system enforces constraints, such as prerequisites for courses and the allocation of classrooms. For example, courses should belong to the department of their instructor, and no two courses should overlap in terms of classroom and time slot. A prerequisite is a course that the student must pass before taking the other course, and the course ID of a prerequisite must be less than the ID of the succeeding course. There is an authentication mechanism in place for logging in, and passwords are encrypted using the SHA256 algorithm and stored in the database accordingly.

You can find the details of the sample database in [create_db.py](https://github.com/salimtirit/SimpleBoun-Registration/blob/main/cmpe321ps/cmpe321ps/create_db.py).

## Requirements ##
* MySQL
* Python(>3.8) and pip module.

If you have these, then run the following code:
```pip install -r requirements.txt```
In order to prevent any possible conflicts, you can set up a virtual environment. You can learn more about virtual environments on [here](https://docs.python.org/3/library/venv.html#module-venv)

## Deployment ##
First, create an .env file in cmpe321ps folder (folder with the settings.py file), and insert:

```
MYSQL_DATABASE=<YOUR_DB_NAME>
MYSQL_USER=<YOUR_USERNAME>
MYSQL_ROOT_PASSWORD=<YOUR_PASSWORD>
MYSQL_PASSWORD=<YOUR_PASSWORD>
MYSQL_HOST="localhost"
```

After that, ensure that your database server is up and run these commands to set up the database to Django configurations:
```
cd cmpe321ps
python manage.py makemigrations
python manage.py migrate
```
This will create some Django related tables on the database (Do not alter them otherwise framework may fail).

Then, you can run this command to create up and fill relevant tables:
``` python cmpe321ps/create_db.py ```

Finally, run the command:
```python manage.py runserver```
and check whether the website is accessible at: [http://127.0.0.1:8000/forum/](http://127.0.0.1:8000/forum/)
