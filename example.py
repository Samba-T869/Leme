from flask import Flask, render_template
import os
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thedaysofthejaguar'
socketio = SocketIO(app)

@app.route('/')
def home():
	return render_template('chat.html')

@socketio.on('new_message')
def handle_message(data):
	sender_id = data.get('sender_id')
	message = data.get('text')
	
	emit('incoming_message', {
	'sender_id': sender_id,
	'text': message,
	'type': 'broadcast'
	}, broadcast =True)

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 9000))
	socketio.run(app, port=port, debug=False)