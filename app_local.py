# Este archivo es para ambientes locales, sin servidores

from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS

import ssl

from socket_events import register_socket_events

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

register_socket_events(socketio)  # Registrar eventos

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    print("iniciando websocket")

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain('certs/fullchain.crt', 'certs/seis.key')

    socketio.run(
        app, 
        host='0.0.0.0', 
        port=5001,
        ssl_context=ssl_context,
        allow_unsafe_werkzeug=True
    )