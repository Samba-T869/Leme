from flask import Flask, render_template
import os
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'thedaysofthejaguar')

#CORS(app)

# Add CORS configuration for Render
socketio = SocketIO(app, 
                   cors_allowed_origins="*",  # Allow all origins (adjust for production)
                   logger=True,  # Enable logging for debugging
                   engineio_logger=True)

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
    }, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 9000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)  # debug=False for production
