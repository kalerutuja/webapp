from flask import Blueprint, request, make_response, jsonify
import re
import bcrypt
from sqlalchemy.sql import func
from flask_httpauth import HTTPBasicAuth
import boto3
from boto3.dynamodb.conditions import Key

from botocore.exceptions import NoCredentialsError, ClientError
import os
import logging
import statsd
import time
import uuid
import json
import http
import hashlib

from datetime import date

import jwt
import datetime
from functools import wraps
from .models import User, Pic
from . import db
from . import webapp

auth = Blueprint('auth', __name__)
salt = bcrypt.gensalt(13)

# For logging
with open('/tmp/records.log', 'w') as f:
    f.write('Starting Application!')
logging.basicConfig(filename='/tmp/records.log', level=logging.DEBUG,
                    format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
logger = logging.getLogger("http.client")
logger.setLevel(logging.DEBUG)
logger.propagate = True

http.client.HTTPConnection.debuglevel = 1


def print_to_log(*args):
    logger.debug(" ".join(args))


http.client.print = print_to_log
c = statsd.StatsClient('localhost', 8125)

with open('/opt/resources') as f:
    credentials = [line.rstrip() for line in f]

bucket_name = credentials[0]
client_s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
sns = boto3.client('sns', region_name='us-east-1')


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']
        if not token:
            return jsonify({'message': 'a valid token is missing'})
        try:
            data = jwt.decode(token, webapp.config['SECRET_KEY'])
            curr_user = User.query.filter_by(uname=data['user']).first()
        except:
            return jsonify({'message': 'token is invalid'})
        return f(curr_user, *args, **kwargs)

    return decorator


@auth.route('/v1/verifyUserEmail', methods=['GET'])
def verifyUser():
    msg = "Verification"
    token = request.args.get('token')
    email = request.args.get('email')
    table = dynamodb.Table('users')
    response = table.query(
        KeyConditionExpression=Key('id').eq(1)
    )
    if response['Items'][0]['EmailAddress'] == email and response['Items'][0]['Token'] == token:
        if response['Items'][0]['ExpirationTime'] > str(int(time.time())):
            verify = User.query.filter_by(uname=User.uname).first()
            verify.verified = "Yes"
            db.session.commit()
            msg = make_response(
                {'success': "User account successfully verified!"}, 200)
        else:
            msg = make_response({'error': "User's token expired!"}, 401)
    else:
        msg = make_response({'error': "Invalid Token!"}, 401)
    return msg


@auth.route('/v1/sign-up', methods=['GET', 'POST'])
def signup():
    msg = "welcome"
    db.create_all()
    db.session.commit()
    email_regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    if request.method == 'GET':
        # dur = (time.time() - start) * 1000
        # c.timing("tasktime", dur)
        # c.incr("taskcount")
        statsd.StatsClient().incr("statsd_Sign-up_GET")
        statsd.StatsClient().timer('statsd_Sign-up_GET', rate=1)

        logger.info("Sending HTTP GET")
        msg = f"Welcome to the Sign up page!"
        return make_response(jsonify({'success': msg}), 200)

    if request.method == 'POST':
        statsd.StatsClient().incr("statsd_Sign-up_POST")
        statsd.StatsClient().timer('statsd_Sign-up_POST', rate=1)

        logger.info("Sending HTTP POST")

        try:
            fname = request.args.get('fname')
            lname = request.args.get('lname')
            uname = request.args.get('uname')
            token = hashlib.md5(uname.encode()).hexdigest()
            expiryTimestamp = int(time.time() + 120)
            table = dynamodb.Table('users')

            if re.search(email_regex, uname):
                user = User.query.filter_by(uname=uname).first()
                if user:
                    msg = make_response(
                        jsonify({'error': 'User already exist!'}), 403)
                else:
                    User.query.delete()
                    db.session.commit()
                    password = request.args.get('password')
                    cpassword = request.args.get('cpassword')
                    if len(password) < 6 or len(password) > 10:
                        msg = make_response(
                            jsonify({'error': 'Password length must be between 6 to 20 characters!'}), 400)
                    elif re.search('[0-9]', password) is None:
                        msg = make_response(
                            jsonify({'error': 'Password must have at least one number!'}), 400)
                    elif re.search('[A-Z]', password) is None:
                        msg = make_response(
                            jsonify({'error': 'Password must have at least one capital letter!'}), 400)
                    elif password != cpassword:
                        msg = make_response(
                            jsonify({'error': 'Password does not match. Please try again!'}), 400)
                    else:
                        hashPassword = bcrypt.hashpw(
                            password.encode('utf-8'), salt)
                        new_user = User(fname=fname, lname=lname,
                                        uname=uname, password=hashPassword)
                        db.create_all()
                        db.session.commit()
                        db.session.add(new_user)
                        db.session.commit()
                        msg = f"Welcome {fname} {lname}, your account has been successfully created!"
                        msg = make_response(jsonify({'success': msg}), 200)

                scan = table.scan()
                with table.batch_writer() as batch:
                    for each in scan['Items']:
                        batch.delete_item(
                            Key={
                                'id': each['id'],
                                'EmailAddress': each['EmailAddress']
                            }
                        )
                # When user creates a new account. Sign-up function puts a dynamodb item with new user details
                table.put_item(
                    Item={
                        'id': 1,
                        'EmailAddress': uname,
                        'Token': str(token),
                        'CreationTime': str(int(time.time())),
                        'ExpirationTime': str(expiryTimestamp)
                    }
                )
                # and then Publish to a SNS Topic. SNS topic will trigger lambda function
                sns.publish(
                    TopicArn='arn:aws:sns:us-east-1:441181477790:prod-sns-topic',
                    Message=json.dumps(
                        {'Email Address': uname, 'Token': str(token), 'CreationTime': str(int(time.time())),
                         'ExpirationTime': str(expiryTimestamp)}))
            else:
                msg = make_response(
                    jsonify({'error': 'Please enter valid Email Address!'}), 400)
        except:
            db.session.rollback()
            msg = make_response(
                jsonify({'error': 'Operation can not complete'}), 400)
    return msg


@auth.route('/v1/login', methods=['GET'])
def login():
    statsd.StatsClient().incr("statsd_login_GET")
    statsd.StatsClient().timer('statsd_login_GET', rate=1)

    logger.info("Sending HTTP GET")
    auth0 = request.authorization
    pswd = auth0.password
    hashpass = bcrypt.hashpw(pswd.encode('utf-8'), salt)
    user = db.session.using_bind('slave').query(
        User).filter_by(uname=auth0.username).first()
    if user:
        result = db.session.using_bind('slave').query(User).filter_by(
            uname=auth0.username, verified="Yes").first()
        print(result)
        if result:
            if not bcrypt.checkpw(user.password, hashpass):
                token = jwt.encode({'user': user.uname, 'exp': datetime.datetime.utcnow(
                ) + datetime.timedelta(minutes=30)}, webapp.config['SECRET_KEY'])
                return make_response(jsonify({'success': "Login Successful!", 'token': token.decode('UTF-8')}))

        else:
            return make_response({'error': "User is not verified!"}, 401,
                                 {'WWW.Authentication': 'Basic realm: "User verification required"'})
    return make_response({'error': "User doesn't exist!"}, 401, {'WWW.Authentication': 'Basic realm: "login required"'})


@auth.route('/v1/user', methods=['GET', 'POST'])
@token_required
def user(curr_user):
    if request.method == 'GET':
        user = db.session.using_bind('slave').query(
            User).filter_by(uname=curr_user.uname).first()
        statsd.StatsClient().incr("statsd_user_GET")
        statsd.StatsClient().timer('statsd_user_GET', rate=1)
        logger.info("Sending HTTP GET")
        try:
            if user:
                msg = make_response(jsonify(
                    {'First Name': user.fname, 'Last Name': user.lname, 'User Name': user.uname,
                     'CreatedAt': user.createdAt,
                     'LastUpdated': user.lastUpdated}), 200)
            else:
                msg = make_response(
                    jsonify({'error': "User doesn't exist!"}), 404)
        except:
            msg = make_response(
                jsonify({'error': 'Operation can not complete'}), 400)

    if request.method == 'POST':
        user = User.query.filter_by(uname=curr_user.uname).first()
        statsd.StatsClient().incr("statsd_user_POST")
        statsd.StatsClient().timer('statsd_user_POST', rate=1)
        logger.info("Sending HTTP POST")

        try:
            if user:
                fname = request.args.get('fname')
                lname = request.args.get('lname')
                password = request.args.get('password')
                cpassword = request.args.get('cpassword')
                if len(password) < 6 or len(password) > 10:
                    msg = make_response(
                        jsonify({'error': 'Password length must be between 6 to 20 characters!'}), 400)
                elif re.search('[0-9]', password) is None:
                    msg = make_response(
                        jsonify({'error': 'Password must have at least one number!'}), 400)
                elif re.search('[A-Z]', password) is None:
                    msg = make_response(
                        jsonify({'error': 'Password must have at least one capital letter!'}), 400)
                elif password != cpassword:
                    msg = make_response(
                        jsonify({'error': 'Password does not match. Please try again!'}), 400)
                else:
                    hashPassword = bcrypt.hashpw(
                        password.encode('utf-8'), salt)
                    update = User.query.filter_by(
                        uname=curr_user.uname).first()
                    update.fname = fname
                    update.lname = lname
                    update.password = hashPassword
                    update.lastUpdated = func.now()
                    db.session.commit()
                    msg = make_response(jsonify(
                        {'success': 'Your account has been successfully updated!', 'First Name': user.fname,
                         'Last Name': user.lname, 'User Name': user.uname, 'CreatedAt': user.createdAt,
                         'LastUpdated': user.lastUpdated}), 200)
        except:
            msg = make_response(
                jsonify({'error': 'Operation can not complete'}), 400)
    return msg


@auth.route('/v1/update', methods=['PUT'])
@token_required
def update(curr_user):
    statsd.StatsClient().incr("statsd_update_PUT")
    statsd.StatsClient().timer('statsd_update_PUT', rate=1)
    logger.info("Sending HTTP PUT")

    webapp.logger.info('Info level log')
    webapp.logger.warning('Warning level log')
    user = User.query.filter_by(uname=curr_user.uname).first()
    if user:
        fname = request.args.get('fname')
        lname = request.args.get('lname')
        password = request.args.get('password')
        cpassword = request.args.get('cpassword')
        if len(password) < 6 or len(password) > 10:
            msg = make_response(
                jsonify({'error': 'Password length must be between 6 to 20 characters!'}), 400)
        elif re.search('[0-9]', password) is None:
            msg = make_response(
                jsonify({'error': 'Password must have at least one number!'}), 400)
        elif re.search('[A-Z]', password) is None:
            msg = make_response(
                jsonify({'error': 'Password must have at least one capital letter!'}), 400)
        elif password != cpassword:
            msg = make_response(
                jsonify({'error': 'Password does not match. Please try again!'}), 400)
        else:
            hashPassword = bcrypt.hashpw(password.encode('utf-8'), salt)
            update = User.query.filter_by(uname=curr_user.uname).first()
            update.fname = fname
            update.lname = lname
            update.password = hashPassword
            update.lastUpdated = func.now()
            db.session.commit()
            msg = make_response(jsonify(
                {'success': 'Your account has been successfully updated!', 'First Name': user.fname,
                 'Last Name': user.lname, 'User Name': user.uname, 'CreatedAt': user.createdAt,
                 'LastUpdated': user.lastUpdated}), 200)
    return msg


@auth.route('/v1/pic', methods=['GET', 'POST', 'DELETE'])
@token_required
def pic(curr_user):
    webapp.logger.info('Info level log')
    webapp.logger.warning('Warning level log')
    msg = "welcome"
    result = []
    user_info = {}
    # db.create_all()
    # db.session.commit()
    data_file_folder = os.path.join(os.getcwd(), 'app/pics')
    file = os.listdir(data_file_folder)[0]

    if request.method == 'POST':
        user = User.query.filter_by(uname=curr_user.uname).first()

        object_name = user.uname + "/" + file
        statsd.StatsClient().incr("statsd_pic_POST")
        statsd.StatsClient().timer('statsd_pic_POST', rate=1)

        logger.info("Sending HTTP POST")
        if user:
            s3 = boto3.resource('s3')
            bucket = s3.Bucket(bucket_name)
            for obj in bucket.objects.filter(Prefix=user.uname + '/'):
                s3.Object(bucket.name, obj.key).delete()
            if object_name is None:
                object_name = os.path.join(data_file_folder, file)
            if not file.startswith('~'):
                try:
                    client_s3.upload_file(
                        os.path.join(data_file_folder, file),
                        bucket_name,
                        object_name
                    )
                    profile_user = Pic.query.filter_by(
                        uname=curr_user.uname).first()
                    head_object = client_s3.head_object(
                        Bucket=bucket_name, Key=object_name)
                    result.append(head_object)
                    if profile_user:
                        profile_user.profile = file
                        profile_user.lastUpdated = func.now()
                        db.session.commit()
                        msg = make_response(jsonify({"success": "User's profile picture successfully updated!",
                                                     'First Name': profile_user.fname, 'Last Name': profile_user.lname,
                                                     'User Name': profile_user.uname,
                                                     'Picture Name': profile_user.profile,
                                                     'CreatedAt': profile_user.createdAt,
                                                     'LastUpdated': profile_user.lastUpdated}), 200)
                    else:
                        profile_user = Pic(
                            fname=user.fname, lname=user.lname, uname=user.uname, profile=file)
                        db.session.add(profile_user)
                        db.session.commit()
                        msg = make_response(jsonify(
                            {"success": "User's profile picture successfully added!", 'First Name': profile_user.fname,
                             'Last Name': profile_user.lname,
                             'User Name': profile_user.uname, 'Picture Name': profile_user.profile,
                             'CreatedAt': profile_user.createdAt, 'LastUpdated': profile_user.lastUpdated}), 200)

                except ClientError as e:
                    msg = make_response(
                        jsonify({'error': 'Login Incorrect'}), e, 400)
        else:
            msg = make_response(jsonify({'error': "User doesn't exist!"}), 404)

    if request.method == 'GET':
        user = db.session.using_bind('slave').query(
            User).filter_by(uname=curr_user.uname).first()
        statsd.StatsClient().incr("statsd_pic_GET")
        statsd.StatsClient().timer('statsd_pic_GET', rate=1)

        logger.info("Sending HTTP GET")
        profile_user = db.session.using_bind('slave').query(
            Pic).filter_by(uname=curr_user.uname).first()
        if user:
            if not profile_user:
                msg = make_response(
                    jsonify({'error': "User doesn't have profile picture!"}), 404)
            else:
                s3 = boto3.resource('s3')
                bucket = s3.Bucket(bucket_name)
                msg = make_response(
                    jsonify({"success": "User has no profile picture assigned!"}), 201)
                for obj in bucket.objects.filter(Prefix=user.uname + '/'):
                    user_info["Image Name"] = bucket.name + "/" + obj.key
                    result.append(bucket.name + "/" + obj.key)
                    msg = make_response(jsonify(
                        {"success": "User's profile picture found!", 'First Name': profile_user.fname,
                         'Last Name': profile_user.lname, 'User Name': profile_user.uname,
                         'Picture Name': profile_user.profile, 'CreatedAt': profile_user.createdAt,
                         'LastUpdated': profile_user.lastUpdated}), 200)
        else:
            msg = make_response(jsonify({'error': "User doesn't exist!"}), 404)

    if request.method == 'DELETE':
        user = User.query.filter_by(uname=curr_user.uname).first()

        statsd.StatsClient().incr("statsd_pic_DELETE")
        statsd.StatsClient().timer('statsd_pic_DELETE', rate=1)
        logger.info("Sending HTTP DELETE")
        profile_user = Pic.query.filter_by(uname=curr_user.uname).first()
        if user:
            if profile_user:
                s3 = boto3.resource('s3')
                bucket = s3.Bucket(bucket_name)
                try:
                    for obj in bucket.objects.filter(Prefix=user.uname + '/'):
                        s3.Object(bucket.name, obj.key).delete()
                        Pic.query.filter(Pic.profile == file).delete()
                        db.session.commit()
                        msg = make_response(
                            jsonify({"success": "User's profile picture successfully deleted!"}), 201)
                except ClientError as e:
                    msg = make_response(
                        jsonify({'error': 'Login Incorrect'}), e, 400)
            else:
                msg = make_response(
                    jsonify({"error": "User has no profile picture assigned!"}), 404)
        else:
            msg = make_response(jsonify({'error': "User doesn't exist!"}), 404)
    return msg


@auth.route('/v1/users', methods=['GET'])
def get_all_users():
    statsd.StatsClient().incr("statsd_users_GET")
    statsd.StatsClient().timer('statsd_users_GET', rate=1)

    logger.info("Sending HTTP GET")
    webapp.logger.info('Info level log')
    webapp.logger.warning('Warning level log')
    users = db.session.using_bind('slave').query(User).all()
    result = []
    for user in users:
        user_data = {'First Name': user.fname, 'Last Name': user.lname, 'User Name': user.uname,
                     'CreatedAt': user.createdAt, 'LastUpdated': user.lastUpdated}
        result.append(user_data)
    return jsonify({'users': result})

# @auth.route('/logout')
# def logout():
#     return "<p>Logout</p>"


#
