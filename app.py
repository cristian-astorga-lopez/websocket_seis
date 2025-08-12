from flask import Flask, jsonify,request
from flask_socketio import SocketIO,join_room, leave_room
from flask_cors import CORS

import ssl

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


#socketio = SocketIO(app, async_mode='gevent', cors_allowed_origins="*")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')


@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@socketio.on('connect')
def handle_connect():
    print("Cliente conectado")

@socketio.on('disconnect')
def handle_disconnect():
    print("Cliente desconectado")

@socketio.on('join_hospital')
def handle_join_hospital(data):
    hospital_id = data.get('hospital')  # ejemplo: "hds"
    join_room(hospital_id)
    print(f"Cliente unido a sala: {hospital_id}")
    socketio.emit('joined', {'hospital': hospital_id}, room=hospital_id)

@socketio.on('mensaje_hospital')
def handle_mensaje_hospital(data):
    hospital_id = data.get('hospital')
    mensaje = data.get('mensaje')
    print(f"Mensaje para {hospital_id}: {mensaje}")

    socketio.emit('respuesta_hospital', {'mensaje': mensaje}, 
    room=hospital_id,
    skip_sid=request.sid  # evita que el emisor lo reciba
    )

if __name__ == "__main__":
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain('certs/cert.pem', 'certs/key.pem')
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=5001,
        allow_unsafe_werkzeug=True
        #ssl_context=ssl_context
    )
