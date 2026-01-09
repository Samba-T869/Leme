from flask import Flask, render_template
import os
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thedaysofthejaguar'
socketio = SocketIO(app)

@app.route('/')
def home():
	return render_template('chat.html')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('new_message')
def handle_message(data):
	sender_id = data.get('sender_id')
	message = data.get('text')
	
	emit('incoming_message', {
	'sender_id': sender_id,
	'text': message,
	'type': 'broadcast'
	}, broadcast =True)
	print(f"message from {sender_id}: {message}")

if __name__ == '__main__':
	socketio.run(app, port=9000, debug=True)