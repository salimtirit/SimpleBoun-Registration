import mysql.connector
import environ
from hashlib import sha256

env = environ.Env()
environ.Env.read_env()

connection = mysql.connector.connect(
  host=env("MYSQL_HOST"),
  user=env("MYSQL_USER"),
  password=env("MYSQL_PASSWORD"),
  database=env("MYSQL_DATABASE"),
  auth_plugin='mysql_native_password'
)

cursor= connection.cursor()
#Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS Department(
	departmentID int,
	name varchar(255) UNIQUE,
	PRIMARY KEY (departmentID)
);""")

cursor.execute("""
CREATE TABLE Student(
	studentID int not null UNIQUE AUTO_INCREMENT,
    GPA FLOAT(24),
    completed_credits int not null,
	username varchar(255),
	password varchar(255) not null,
	name varchar(255),
	surname	varchar(255),
	email varchar(255),
	departmentID int,
	PRIMARY KEY (username),
	FOREIGN KEY (departmentID) REFERENCES Department(departmentID)
		ON UPDATE CASCADE
		ON DELETE SET NULL
);""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Instructor(
	username varchar(255),
	title varchar(255),
	password varchar(255),
	name varchar(255),
	surname	varchar(255),
	email varchar(255),
	departmentID int,
	PRIMARY KEY (username),	
	FOREIGN KEY (departmentID) REFERENCES Department(departmentID)
		ON UPDATE CASCADE
		ON DELETE SET NULL
);""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Classroom(
	classroomID int,
	campus varchar(255),
	capacity int,
	PRIMARY KEY (classroomID)
);""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Course(
	courseID varchar(255),
	name varchar(255),
	departmentID int,
	credits int,
	instructor_username varchar(255),
	classroomID int,
	quota int,
	PRIMARY KEY (courseID),
	FOREIGN KEY (departmentID) REFERENCES Department(departmentID)
		ON UPDATE CASCADE
		ON DELETE CASCADE,
	FOREIGN KEY (instructor_username) REFERENCES Instructor(username)
		ON UPDATE CASCADE
		ON DELETE CASCADE,
	FOREIGN KEY (classroomID) REFERENCES Classroom(classroomID)
		ON UPDATE CASCADE
		ON DELETE SET NULL
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Prerequisite_of(
  subsequent varchar(255),
	prerequisite varchar(255),
	PRIMARY KEY(subsequent,prerequisite),
    FOREIGN KEY(subsequent) REFERENCES Course(courseID),
    CONSTRAINT check_prereq
		CHECK (prerequisite < subsequent)
);""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Lectured_In(
	courseID varchar(255) UNIQUE,
	classroomID int,
	time_slot int,
	PRIMARY KEY(classroomID,time_slot),
	FOREIGN KEY(courseID) REFERENCES Course(courseID)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	FOREIGN KEY(classroomID) REFERENCES Classroom(classroomID)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	CONSTRAINT check_time_slot
		CHECK (time_slot <= 10)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Enrolled(
	studentID int,
	courseID varchar(255),
	PRIMARY KEY(studentID,courseID),
	FOREIGN KEY(studentID) REFERENCES Student(studentID)
		ON UPDATE CASCADE
		ON DELETE CASCADE,
	FOREIGN KEY(courseID) REFERENCES Course(courseID)
		ON UPDATE CASCADE
		ON DELETE CASCADE
);""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Grades(
	studentID int,
	courseID varchar(255),
	grade FLOAT(24),
	PRIMARY KEY(studentID,courseID),
	FOREIGN KEY(studentID) REFERENCES Student(studentID)
		ON UPDATE CASCADE
		ON DELETE CASCADE,
	FOREIGN KEY(courseID) REFERENCES Course(courseID)
		ON UPDATE CASCADE
		ON DELETE NO ACTION,
	CONSTRAINT check_grade_upper
		CHECK (grade <= 4.0),
	CONSTRAINT check_grade_lower
		CHECK (grade >= 0.0)
);""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS DatabaseManager(
	username varchar(255),
	password varchar(255),
    PRIMARY KEY(username)
);""")


cursor.execute("""
CREATE TRIGGER instructor_username BEFORE INSERT ON Instructor
	FOR EACH ROW
		IF NEW.username in (
			select S.username
            from Student S
		) THEN
			SIGNAL SQLSTATE '50001' SET MESSAGE_TEXT = 'INSERT NOT ALLOWED WITH SAME USERNAME';
		END IF;""")

cursor.execute("""
CREATE TRIGGER student_username BEFORE INSERT ON Student
	FOR EACH ROW
		IF NEW.username in (
			select I.username
            from Instructor I
		) THEN
			SIGNAL SQLSTATE '50001' SET MESSAGE_TEXT = 'INSERT NOT ALLOWED WITH SAME USERNAME';
		END IF;""")

cursor.execute("""
CREATE TRIGGER same_department_id BEFORE INSERT ON COURSE
	FOR EACH ROW
		IF NEW.departmentID != (
			SELECT I.departmentID
            FROM Instructor I
            WHERE NEW.instructor_username = I.username
		) THEN
			SIGNAL SQLSTATE '50001' SET MESSAGE_TEXT = 'INSERT NOT ALLOWED WITH DIFFERENT DEPARTMENT ID FROM INSTRUCTOR';
		END IF; """)

cursor.execute("""
CREATE TRIGGER n_of_dbmanagers BEFORE INSERT ON DatabaseManager
	FOR EACH ROW
		IF (SELECT COUNT(*)
			FROM DatabaseManager) >= 4
		THEN
			SIGNAL SQLSTATE '50001' SET MESSAGE_TEXT = 'THERE CAN BE AT MOST FOUR DATABASE MANAGERS';
		END IF;""")

cursor.execute("""
CREATE TRIGGER 	quota_restriction BEFORE INSERT ON Enrolled
	FOR EACH ROW
		IF (SELECT COUNT(*)
			FROM Enrolled
            WHERE CourseID = NEW.CourseID) >= (SELECT quota FROM Course WHERE CourseID = NEW.CourseID)
		THEN
			SIGNAL SQLSTATE '50001' SET MESSAGE_TEXT = 'THIS COURSE HAS NO QUOTA AVAILABLE';
		END IF;""")

cursor.execute("""
CREATE TRIGGER 	classroom_capacity BEFORE INSERT ON Course
	FOR EACH ROW
		IF (SELECT capacity
			FROM Classroom
            WHERE classroomID = NEW.classroomID) < NEW.quota
		THEN
			SIGNAL SQLSTATE '50001' SET MESSAGE_TEXT = 'THIS CLASSROOM IS TOO SMALL FOR THIS COURSE';
		END IF;""")

cursor.execute("""
CREATE TRIGGER 	adjust_gpa AFTER INSERT ON Grades
	FOR EACH ROW 
    BEGIN
		DECLARE comp_cred INT;
        DECLARE current_gpa FLOAT(24);
        SET comp_cred = (SELECT completed_credits FROM Student WHERE studentID= NEW.studentID);
        SET current_gpa = (SELECT GPA FROM Student WHERE studentID= NEW.studentID);
        
        
        UPDATE Student
		SET 
        GPA = ((comp_cred*current_gpa) + ((SELECT credits FROM Course WHERE CourseID = NEW.CourseID) * NEW.grade)) / (comp_cred+(SELECT credits FROM Course WHERE CourseID = NEW.CourseID)),
		completed_credits = (SELECT credits FROM Course WHERE CourseID = NEW.CourseID) + comp_cred
		WHERE 
			studentID = NEW.studentID; END
""")

cursor.execute("""
CREATE PROCEDURE FilterCourses(IN department_id int, IN campus_ varchar(255), IN min_credits int, IN max_credits int)
BEGIN
SELECT * FROM Course c
WHERE c.departmentID = department_id 
	AND (SELECT campus FROM Classroom WHERE c.classroomID = classroomID) = campus_ 
    AND c.credits <= max_credits
    AND c.credits >= min_credits;
END;""")

cursor.execute("""
CREATE PROCEDURE CreateStudent(IN username varchar(255), IN password varchar(255), IN name varchar(255), IN surname varchar(255), IN email varchar(255), IN departmentID int)
BEGIN
INSERT INTO Student VALUES (0, 0, 0, username, password, name, surname, email, departmentID);
END;
""")

cursor.execute("""
CREATE PROCEDURE CreateInstructor(IN username varchar(255), IN title varchar(255), IN password varchar(255), IN name varchar(255), IN surname	varchar(255), IN email varchar(255), IN departmentID int)
BEGIN
INSERT INTO Instructor VALUES (username,title,password,name,surname,email,departmentID);
END;
""")

cursor.execute("""
CREATE PROCEDURE CreateCourse(IN courseID int, IN name varchar(255), IN departmentID int, IN credits int, IN instructor_username varchar(255), IN classroomID int, IN quota int)
BEGIN
INSERT INTO Course VALUES (courseID, name, departmentID, credits, instructor_username, classroomID, quota);
END;
""")


connection.commit()


cursor.execute("""
INSERT INTO Department VALUES (1,'cmpe');
""")
cursor.execute("""
INSERT INTO Department VALUES (2,'ie');
""")
cursor.execute("""
INSERT INTO Department VALUES (3,'ee');
""")

password = sha256("12345".encode("utf-8")).hexdigest()

cursor.execute(f"""
INSERT INTO Student VALUES (1, 3.4, 0, 'Salim', '{password}', 'Salim', 'Tirit', 'salim.tirit@gmail.com', 1)
""")

cursor.execute(f"""
INSERT INTO Student VALUES (2, 3.3, 0, 'Ahmet', '{password}', 'Ahmet', 'Tirit', 'ahmet.tirit@gmail.com', 2)
""")

cursor.execute(f"""
INSERT INTO Instructor VALUES ('Sami', 'Professor' ,'{password}', 'Sami', 'Tirit', 'sami.tirit@gmail.com', 1)
""")

cursor.execute(f"""
INSERT INTO Instructor VALUES ('Kevser', 'Professor' ,'{password}', 'Kevser', 'Tirit', 'kevser.tirit@gmail.com', 3)
""")

cursor.execute("""
INSERT INTO Classroom VALUES (1, 'Guney', 22)
""")


cursor.execute("""
INSERT INTO Classroom VALUES (2, 'Kuzey', 223)
""")


cursor.execute("""
INSERT INTO Course VALUES (1, 'CMPE321', 1, 5, 'Sami', 2, 100)
""")


cursor.execute("""
INSERT INTO Course VALUES (2, 'EE101', 3, 5, 'Kevser', 1, 10)
""")

password = sha256("admin".encode("utf-8")).hexdigest()
cursor.execute(f"""
INSERT INTO databasemanager VALUES ('admin','{password}');
""")

connection.commit()

#Create the trigger for limiting 5 posts per user
# cursor.execute("""
# CREATE TRIGGER PostInsert
# BEFORE INSERT ON Post
# FOR EACH ROW
# BEGIN
#     IF ( SELECT COUNT(*) FROM Post  WHERE poster = new.poster GROUP BY poster) = 5 THEN 
#     SIGNAL SQLSTATE '45000';
#     END IF;
# END;""")

#Create a stored procedure
# cursor.execute("""
# CREATE PROCEDURE CreatePost(IN title TEXT, IN body TEXT, IN poster VARCHAR(200))
# BEGIN
# INSERT INTO Post VALUES (title,body,poster);
# END;
# """)

# connection.commit()

# cursor.execute('INSERT INTO User VALUES ("berke.argin","123abc");')
# cursor.execute('INSERT INTO User VALUES ("niyazi.ulke","password");')
# cursor.execute('INSERT INTO Post VALUES ("Post1","Post 1 of berke.argin","berke.argin");')
# cursor.execute('INSERT INTO Post VALUES ("Post2","Post 2 of berke.argin","berke.argin");')
# cursor.execute('INSERT INTO Post VALUES ("Post3","Post 3 of berke.argin","berke.argin");')

# connection.commit()
