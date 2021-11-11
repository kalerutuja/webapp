# CSYE - 6225 (Image Resizer API)

==================================

## Getting Started

Following prerequisite steps are required inn order to setup working environment for the application.

### Prerequisites

1. OS: Ubuntu 20.4 LTS
   1. sudo apt update
   2. sudo apt upgrade
2. Mysql
   1. sudo apt install mysql-server
   2. sudo mysql_secure_installation
   3. Create separate database user and make sure you grant appropriate permissions.
   4. sudo apt-get install libmysqlclient-dev
   5. sudo apt-get install -y python3-mysqldb
3. Install pip3
   1. sudo apt install python3-pip
4. Install Flask Framework package
   1. pip3 install flask
   2. pip3 install flask-login
5. Install SQLAlchemy Object Relational Mapper (ORM) package
   1. pip install flask-sqlalchemy
6. Also, install bcrypt package to encrypt user passwords.
   1. pip3 install py-bcrypt

### How to use

1. Create an EC2 instance of Ubuntu 20.4 LTS or higher on AWS, make sure port 8080 and 22 are open for incoming traffic. Also, make note of Public IP address of the instance.

2. Run following mysql query command to create 'webapp' database.

```
CREATE DATABASE webapp;
```

3. Run following commands

```
-	git clone git@github.com:Rutuja-Kale-CYSE6225/webapp.git
-	cd webapp
-	python3 main.py
```

4. Once the app server starts, open Postman API website on your local machine and enter http://<EC2 instance public IP>:8080 to check following scenarios.

   **1. Sign up a new user API: http://<EC2 instance public IP>:8080/sign-up**\

   - Accepts both GET and POST requests\
   - GET method simply returns "Welcome to the Sign up page!" message with success code 200 whereas, POST method creates user accounts.\
   - Create new user with user details like, first name, last name, user name (email), password, and confirm password.\
   - If the user already exists then it will print "error": "User already exist!" along with 400 Bad Request error code.\
   - Else it will check if entered field are valid or not.\
   - It also performs basic password validations like password and confirm passwords match, password is at least 6 charasters long,\ password contain at least one number and a capital letter, etc.\
   - Passwords are generated using bcrypt encoded hash and salt for encryption.\
   - User creation and last updated datetime fields automatically gets added to the user on successful user account creation.\

   **2. Update existing user API: http://<EC2 instance public IP>:8080/update**\

- Accepts both GET and POST requests\
  - GET method simply returns "Welcome to the Update page!" message with success code 200 whereas, POST method updates user account.\
  - Update API allows to modify only first name, last name, and, password fields. User can't modify other fields.\
  - Whenever there is successful modification to the user account, lastUpdated field autmatically gets updated with current datetime.\
  - If user try to update non existing user account, API returns 'error': 'User does not exist!' error message along with 400 Bad Request error code.\

**3. Get a specific user details API: http://<EC2 instance public IP>:8080/user**\

- Accepts both GET and POST requests\
  - GET method simply returns "Welcome to the User page!" message with success code 200 whereas, POST method returns requested user information.\
  - API returns only first name, last name, createdAt and, lastUpdated fields.\
  - API doesn't return protected fields like password.\
  - If user try to find non existing user account, API returns 'error': 'User does not exist!' error message along with 400 Bad Request error code.\

**4. Get a list of all users API: http://<EC2 instance public IP>:8080/user**\

- Accepts only GET request\
  - GET method simply returns all the users created so far with success code 200 whereas.\
  - API returns only first name, last name, createdAt and, lastUpdated fields.\
  - API doesn't return protected fields like password.\

5. Also added Unit test to perform index and status code checks.

## Built With

- [Python3](https://www.python.org/) - Python is an interpreted high-level general-purpose programming language.

- [Flask](https://flask.palletsprojects.com/en/2.0.x/) - Flask is a micro web framework written in Python.

- [MySQL](https://www.mysql.com/) - MySQL is the world's most popular open source database. With its proven performance, reliability and ease-of-use, MySQL has become the leading database choice for web-based applications, used by high profile web properties including Facebook, Twitter, YouTube, Yahoo! and many more.

- [bcrypt](https://www.npmjs.com/package/bcrypt) - A library to help you hash passwords.

- [SQLAlchemy](https://www.sqlalchemy.org/) - SQLAlchemy is the Python SQL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL.

## Versioning

We use [github](https://github.com/) for versioning. For the versions available, see the [tags on this repository](https://github.com/Rutuja-Kale-CYSE6225/webapp).

## Thank you
Updating for Demo
