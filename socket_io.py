from flask_socketio import SocketIO, emit,ConnectionRefusedError, Namespace , join_room, leave_room , send , emit
from flask import jsonify ,json
from main import app
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity,decode_token,create_refresh_token,jwt_refresh_token_required,
    set_access_cookies,set_refresh_cookies,verify_jwt_in_request
)
socketio = SocketIO(app)

class Chat(Namespace):
    def on_connect(self):
        pass
    def on_disconnect(self):
        pass

    def on_join(self,data):
        room = data['room']
        join_room(room)
        print(room + ' a user entered')

class GroupChat(Namespace):
    def on_connect(self):
        print("A User Connected to GroupChat")
    def on_disconnect(self):
        print("User Disconnected")
    def on_join(self,data):
        token = data['token']
        room = data['room']
        try: 
            decode_token(token)
        except:
            raise ConnectionAbortedError('unAuthorized!!')
        join_room(room)
        send("A User is connected",room=room)
    def on_send_message(self,data):
        jsonencoded = json.dumps(data)
        print(jsonencoded)
        emit('receive_message',jsonencoded,room=data['room'])
    


    

