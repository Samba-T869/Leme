import os
from flask import Flask, jsonify, render_template
from flask_sock import Sock
import eventlet
eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
sock = Sock(app)

# Store connected clients
connected_clients = set()

# Serve the HTML page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def status():
    return jsonify({
        'status': 'online',
        'clients': len(connected_clients),
        'message': 'WebSocket server is running'
    })

@sock.route('/ws')
def handle_websocket(ws):
    connected_clients.add(ws)
    client_count = len(connected_clients)
    print(f"New client connected. Total clients: {client_count}")
    
    # Send welcome message
    ws.send(f"Welcome! Connected to server. Total users: {client_count}")
    
    try:
        while True:
            message = ws.receive()
            if message is None:
                break
                
            print(f"Received message: {message}")
            
            # Broadcast to all connected clients except sender
            disconnected_clients = set()
            for client in connected_clients:
                if client != ws:
                    try:
                        client.send(message)
                    except Exception as e:
                        print(f"Error sending to client: {e}")
                        disconnected_clients.add(client)
            
            # Clean up disconnected clients
            for client in disconnected_clients:
                connected_clients.remove(client)
            
            # Confirm to sender
            ws.send(f"You: {message}")
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if ws in connected_clients:
            connected_clients.remove(ws)
        print(f"Client disconnected. Total clients: {len(connected_clients)}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    # Use eventlet for production
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', port)), app)