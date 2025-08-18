from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS

import ssl

from socket_events import register_socket_events

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

#socketio = SocketIO(app, async_mode='gevent', cors_allowed_origins="*")
#async_mode='threading'
async_mode='eventlet'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
print(f"Async mode: {socketio.async_mode}")

register_socket_events(socketio)  # Registrar eventos

@app.route('/')
def index():
    return jsonify({"message": "Servidor WebSocket activo"})

@app.route('/health')
def health():
    return jsonify({"status": "ok"})


"""
Nota: no hace falta el socketio.run ya que el gunicore se encarga de levantarlo, 
el socketio.run es solo para ambientes localtes
"""

if __name__ == "__main__":
    print("iniciando websocket")
    