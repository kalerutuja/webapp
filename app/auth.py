from flask import Blueprint, request, make_response, jsonify
import re
import bcrypt
from sqlalchemy.sql import func
import jwt
from functools import wraps
from .models import User
from . import db
from app import create_app

auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    # uname = request.args.get('uname')
    # password = request.args.get('password')
    # user = User.query.filter_by(uname=uname).first()
    # print(uname, password,user)
    # try:
    #     if user:
    #         salt = bcrypt.gensalt(rounds=8)
    #         hashpass = bcrypt.hashpw(password.encode('utf8'), salt)
    #         if bcrypt.checkpw(user.password, hashpass):
    #             msg = f"Welcome {user.fname} {user.lname}"
    #             msg = make_response(jsonify({'success': msg}), 200)
    #         else:
    #             msg = make_response(jsonify({'error': "Password doesn't match. Please try again!"}), 403)
    #     else:
    #         msg = make_response(jsonify({'error': "User doesn't exist!"}), 404)
    # except:
    #     msg = make_response(jsonify({'error': "Unknown error"}), 403)
    # return msg

@auth.route('/user', methods = ['GET','POST'])
def get_user():
    msg = 'welcome'
    if request.method == 'GET':
        msg = f"Welcome to the User page!"
        return make_response(jsonify({'success': msg}), 200)
    if request.method == 'POST':
        try:
            uname = request.args.get('uname')
            user = User.query.filter_by(uname=uname).first()
            if user:
                msg = make_response(jsonify({'First Name': user.fname, 'Last Name': user.lname,'User Name': user.uname, 'CreatedAt': user.createdAt, 'LastUpdated': user.lastUpdated}), 200)
            else:
                msg = make_response(jsonify({'error': "User doesn't exist!"}), 404)
        except:
            msg = make_response(jsonify({'error': "Unknown error"}), 403)
    return msg


@auth.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    result = []
    for user in users:
        user_data = {}
        user_data['First Name'] = user.fname
        user_data['Last Name'] = user.lname
        user_data['User Name'] = user.uname
        user_data['CreatedAt'] = user.createdAt
        user_data['LastUpdated'] = user.lastUpdated
        result.append(user_data)
    return jsonify({'users': result})

@auth.route('/logout')
def logout():
    return "<p>Logout</p>"

@auth.route('/sign-up', methods=['GET','POST'])
def signup():
    msg = "welcome"
    if request.method == 'GET':
        msg = f"Welcome to the Sign up page!"
        return make_response(jsonify({'success':msg}),200)
    if request.method == 'POST':
        try:
            fname = request.args.get('fname')
            lname = request.args.get('lname')
            uname = request.args.get('uname')
            user = User.query.filter_by(uname=uname).first()
            if user:
                msg = make_response(jsonify({'error': 'User already exist!'}), 403)
            else:
                password = request.args.get('password')
                cpassword = request.args.get('cpassword')
                if len(password) < 6 or len(password) > 10:
                    msg = make_response(jsonify({'error': 'Password length must be between 6 to 20 characters!'}), 401)
                elif re.search('[0-9]', password) is None:
                    msg = make_response(jsonify({'error': 'Password must have at least one number!'}),401)
                elif re.search('[A-Z]', password) is None:
                    msg = make_response(jsonify({'error': 'Password must have at least one capital letter!'}), 401)
                elif password != cpassword:
                    msg = make_response(jsonify({'error': 'Password does not match. Please try again!'}), 401)
                else:
                    salt = bcrypt.gensalt(rounds=8)
                    hashPassword = bcrypt.hashpw(password.encode('utf8'), salt)
                    new_user = User(fname=fname, lname=lname, uname=uname, password=hashPassword)
                    db.create_all()
                    db.session.commit()
                    db.session.add(new_user)
                    db.session.commit()
                    msg = f"Welcome {fname} {lname}, your account has been successfully created!"
                    msg = make_response(jsonify({'success': msg}), 200)
        except:
            db.session.rollback()
            msg = make_response(jsonify({'error': 'Operation can not complete'}), 403)
    return msg


@auth.route('/update', methods=['GET', 'POST'])
def update():
    msg = "welcome"
    if request.method == 'GET':
        msg = f"Welcome to the Update page!"
        return make_response(jsonify({'success':msg}),200)
    if request.method == 'POST':
        # try:
        uname = request.args.get('uname')
        user = User.query.filter_by(uname=uname).first()
        if user:
            fname = request.args.get('fname')
            lname = request.args.get('lname')
            password = request.args.get('password')
            cpassword = request.args.get('cpassword')
            createdAt = request.args.get('createdAt')
            lastUpdated = request.args.get('lastUpdated')
            if len(password) < 6 or len(password) > 10:
                msg = make_response(jsonify({'error': 'Password length must be between 6 to 20 characters!'}), 401)
            elif re.search('[0-9]', password) is None:
                msg = make_response(jsonify({'error': 'Password must have at least one number!'}),401)
            elif re.search('[A-Z]', password) is None:
                msg = make_response(jsonify({'error': 'Password must have at least one capital letter!'}), 401)
            elif password != cpassword:
                msg = make_response(jsonify({'error': 'Password does not match. Please try again!'}), 401)
            else:
                # if createdAt != None or lastUpdated != None:
                #     msg = make_response(jsonify({'error': 'Bad Request!'}), 403)
                # else:
                salt = bcrypt.gensalt(rounds=8)
                hashPassword = bcrypt.hashpw(password.encode('utf8'), salt)
                update = User.query.filter_by(uname=uname).first()
                update.fname = fname
                update.lname = lname
                update.password = hashPassword
                update.lastUpdated = func.now()
                db.session.commit()
                msg = make_response(jsonify({'success': 'Your account has been successfully updated!', 'First Name': user.fname, 'Last Name': user.lname,'User Name': user.uname, 'CreatedAt': user.createdAt, 'LastUpdated': user.lastUpdated}), 200)
        else:
            msg = make_response(jsonify({'error': 'User does not exist!'}), 404)
        #
        # except:
        #     db.session.rollback()
        #     msg = make_response(jsonify({'error': 'Operation can not complete'}), 403)
    return msg

#
# def token_required(f):
#     @wraps(f)
#     def decorator(*args, **kwargs):
#         token = None
#         if 'x-access-tokens' in request.headers:
#             token = request.headers['x-access-tokens']
#         if not token:
#             return jsonify({'message': 'a valid token is missing'})
#         try:
#             data = jwt.decode(token, create_app.webapp.config['SECRET_KEY'], algorithms=["HS256"])
#             current_user = User.query.filter_by(public_id=data['public_id']).first()
#         except:
#             return jsonify({'message': 'token is invalid'})
#
#         return f(current_user, *args, **kwargs)
#
#     return decorator