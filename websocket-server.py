from flask import Flask, request
from flask_socketio import SocketIO, emit
import json

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')

# Endpoint to receive message from GSM module
@app.route('/receive_message', methods=['POST'])
def receive_message():
    message_data = request.get_json()
    print("Received message from GSM module:", message_data)
    socketio.emit('receive_message', message_data)  # Emit message to connected clients
    return 'Message received successfully'

if __name__ == '__main__':
    socketio.run(app, host='192.168.1.239', port=8765)