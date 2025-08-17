import eventlet
eventlet.monkey_patch()

import eventlet.wsgi

import ssl

from flask import Flask, jsonify,request
from flask_socketio import SocketIO,join_room, leave_room
from flask_cors import CORS

from socketio import WSGIApp

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

#socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
socketio = SocketIO(app, cors_allowed_origins="*")

blocked_rooms = {}  # clave: nombre de sala, valor: dict con sid, user_id, nombre

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@socketio.on('connect')
def handle_connect():
    print("Cliente conectado")

@socketio.on('disconnect')
def handle_disconnect(sid):
    #sid = request.sid

    rooms_to_be_enabled = [room for room, info in blocked_rooms.items() if info['sid'] == sid]

    for room in rooms_to_be_enabled:
        nombre = blocked_rooms[room]['data'].get('nombre', 'desconocido')
        del blocked_rooms[room]
        print(f"Sala {room} liberada por desconexión de {nombre} ({sid})")


    print("Cliente desconectado")

@socketio.on('join_room')
def handle_join_room(sid,data):
    room_id = data.get('room_id')  # ejemplo: "hds"
    exclusive = data.get('exclusive')
    #sid = request.sid

    if not room_id:
        print("room_id no proporcionado")
        return

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
    if room_id in blocked_rooms:
        socketio.emit('you_joined_room', data, to=sid)
    else:
        socketio.emit('joined_room', data, room=room_id)

@socketio.on('leave_room')
def handle_leave_room(sid,data):
    #sid = request.sid
    room_id = data.get('room_id')  # ejemplo: "hds"

    if not room_id:
        print("room_id no proporcionado")
        return

    exclusive = room_id in blocked_rooms

    if room_id in blocked_rooms and blocked_rooms[room_id]['sid'] == sid:
        del blocked_rooms[room_id]
    else:
        print(f"La sala {room_id} no está bloqueada por este cliente.")

    leave_room(room_id)
    print(f"Cliente abandona la sala: {room_id}")

    if exclusive:
        socketio.emit('you_leaved_room', data, to=sid)
    else:
        socketio.emit('leaved_room', data, room=room_id)

@socketio.on('mensaje_hospital')
def handle_mensaje_hospital(sid,data):
    #sid = request.sid

    hospital_id = data.get('hospital')
    mensaje = data.get('mensaje')

    print(f"Mensaje para {hospital_id}: {mensaje}")

    socketio.emit('respuesta_hospital', {'mensaje': mensaje}, 
        room=hospital_id,
        skip_sid=sid  # evita que el emisor lo reciba
    )

ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain('certs/fullchain.crt', 'certs/seis.key')

if __name__ == "__main__":
    print("iniciando websocket")
    

    """
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=5001,
        ssl_context=ssl_context
        #allow_unsafe_werkzeug=True
    )"""

    listener = eventlet.listen(('0.0.0.0', 5001))
    ssl_listener = ssl_context.wrap_socket(listener, server_side=True)

    wsgi_app = WSGIApp(socketio, app)

    eventlet.wsgi.server(ssl_listener, wsgi_app)
