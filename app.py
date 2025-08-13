from flask import Flask, jsonify,request
from flask_socketio import SocketIO,join_room, leave_room
from flask_cors import CORS

import ssl

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

#socketio = SocketIO(app, async_mode='gevent', cors_allowed_origins="*")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

blocked_rooms = {}  # clave: nombre de sala, valor: dict con sid, user_id, nombre


@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@socketio.on('connect')
def handle_connect():
    print("Cliente conectado")

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid

    rooms_to_be_enabled = [room for room, info in blocked_rooms.items() if info['sid'] == sid]

    for room in rooms_to_be_enabled:
        nombre = blocked_rooms[room]['data'].get('nombre', 'desconocido')
        del blocked_rooms[room]
        print(f"Sala {room} liberada por desconexión de {nombre} ({sid})")


    print("Cliente desconectado")

@socketio.on('join_room')
def handle_join_room(data):
    room_id = data.get('room_id')  # ejemplo: "hds"
    exclusive = data.get('exclusive')
    sid = request.sid

    if room_id in blocked_rooms:

        data_blocked_room = blocked_rooms[room_id]['data']
        socketio.emit('blocked_room', data_blocked_room, to=sid)
        print(f"Intento de ingreso rechazado: sala {room_id} ya ocupada")
        return

    if exclusive == "1":
        blocked_rooms[room_id] = {
            'sid': sid,
            'data': data
        }


    join_room(room_id)
    print(f"Cliente unido a sala: {room_id}")
    socketio.emit('joined_room', {'hospital': room_id}, room=room_id)

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
    print("iniciando websocket")
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    #ssl_context.load_cert_chain('certs/cert.pem', 'certs/key.pem')
    ssl_context.load_cert_chain('certs/fullchain.crt', 'certs/seis.key')

    socketio.run(
        app, 
        host='0.0.0.0', 
        port=5001,
        ssl_context=ssl_context,
        allow_unsafe_werkzeug=True
        #ssl_context=ssl_context
    )
