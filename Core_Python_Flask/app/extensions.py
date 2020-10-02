import redis
from flask_socketio import SocketIO
from webargs.flaskparser import FlaskParser
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_redis import FlaskRedis
from logging.handlers import RotatingFileHandler
from flask_socketio import send, emit, join_room, leave_room
from flask import request
import pandas

users_login = {}

pd = pandas
parser = FlaskParser()
jwt = JWTManager()
client = SQLAlchemy()
redis_store = FlaskRedis()
app_log_handler = RotatingFileHandler('logs/app.log', maxBytes=1000000, backupCount=30)
# red = redis.StrictRedis(host='localhost', password='1234567a@')
red = redis.StrictRedis(host='localhost')
# red = redis.StrictRedis(host='redis', port=6379, decode_responses=True)
socketio = SocketIO(async_mode='eventlet',cors_allowed_origins="*")


@socketio.on(message='connect')
def test_connect():
    print('[CONNECTED] ' + request.sid)


# The connection event handler can return False to reject the connection, or it can also raise ConectionRefusedError
@socketio.on(message='connect', namespace='/message2')
def test_connect():
    print('[CONNECTED MESSAGE2] ' + request.sid)


# Disconnect event when client run socket.disconnect();
@socketio.on(message='disconnect')
def test_disconnect():
    print('[DISCONNECTED] ' + request.sid)
    print(users_login)


# a user when connect to this socket will have a session ID of the connection which can be obtained from request.sid
# this function will store all users in a dictionary with username and the session ID of the connection
@socketio.on(message='login')
def login(username):
    users_login[username] = request.sid
    print(username + ' Login')


# broadcast=True When a message is sent with the broadcast option enabled, all clients connected
# to the namespace receive it, including the sender. When namespaces are not used, the clients
# connected to the global namespace receive the message
@socketio.on(message='message')
def handle_message(msg):
    send(msg, broadcast=True)


# a session ID of the connection is a room contain this user, this function will get session id of the receiver user
# from dictionary users, then emit event new_private_msg with parameter room=receive_session_id
@socketio.on(message='chat_private')
def chat_private(data):
    receive_session_id = users_login[data['username']]
    message = data['message']
    emit('new_private_msg', message, room=receive_session_id)


# room=room all clients join this room will receive it
@socketio.on(message='chat_group')
def chat_group(data):
    room = data['room']
    sender = data['username']
    message = sender + ': ' + data['message']
    emit('new_group_msg', message, room=room)


@socketio.on(message='join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    emit('msg_room', username + ' has entered the room.' + room.upper(), room=room)


@socketio.on(message='leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    emit('msg_room', username + ' has left the room ' + room.upper(), room=room)


# Default namespace is '/', connect io.connect('http://127.0.0.1:5000')
# a name space have many rooms, connect io('http://127.0.0.1:5000/message2');
@socketio.on(message='join2', namespace='/message2')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    emit('msg_room', username + ' has entered the room.' + room.upper(), room=room, namespace='/message2')


@socketio.on(message='message', namespace='/message2')
def on_message2(msg):
    send(msg, room='AI', namespace='/message2')