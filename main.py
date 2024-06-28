from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, send, join_room, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

rooms = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_room', methods=['POST'])
def create_room():
    room = request.form['room']
    password = request.form.get('password', '')
    if room in rooms:
        return 'Room already exists', 400
    rooms[room] = {'users': [], 'password': password}
    return 'Room created', 200

@app.route('/join_room', methods=['POST'])
def join_existing_room():
    room = request.form['room']
    password = request.form.get('password', '')
    username = request.form['username']  # Added to get username from request
    if room not in rooms:
        return 'Room does not exist', 400
    if rooms[room]['password'] and rooms[room]['password'] != password:
        return 'Incorrect password', 400
    if username in rooms[room]['users']:
        return 'Username already exists in the room', 400
    return 'Room joined', 200


@app.route('/get_rooms', methods=['GET'])
def get_rooms():
    username = request.args.get('username')
    public_rooms = []
    for room, details in rooms.items():
        if not details['password']:
            if username not in details['users']:
                public_rooms.append(room)
    return jsonify(public_rooms)


@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    rooms[room]['users'].append(username)
    send(f'{username} has entered the room.', to=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    if username in rooms[room]['users']:
        rooms[room]['users'].remove(username)
    send(f'{username} has left the room.', to=room)

@socketio.on('message')
def handle_message(data):
    room = data['room']
    send(f'{data["username"]}: {data["message"]}', to=room)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
