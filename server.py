from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    print(f'User connected: {request.sid}')

@socketio.on('send_message')
def handle_send_message(data):
    print(data);
    time.sleep(3)
    emit('receive_message', "Pakyu from Orange Pi")

if __name__ == '__main__':
    # Make sure to replace '0.0.0.0' with the actual IP address of your Orange Pi
    socketio.run(app, host='192.168.1.239', port=8765)