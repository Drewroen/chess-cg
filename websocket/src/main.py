#!/usr/bin/env python3

import obj.chess as chess
from obj.objects import Piece, Position
import obj.room as gameRoom

from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*", allow_eio3=True)


player_rooms = {}
rooms = {}


@socketio.on("connect")
def test_connect():
    if request.sid not in player_rooms:
        for room_id in rooms:
            room = rooms[room_id]
            if room.open():
                player_rooms[request.sid] = room
                join_room(room_id)
                room.join(request.sid)
                break
        else:
            room = gameRoom.Room()
            rooms[room.id] = room
            player_rooms[request.sid] = room
    else:
        room = player_rooms[request.sid]

    print(request.sid + " connected to room " + str(room.id))
    emit("board", {"squares": room.board.get_squares()}, to=room.id)


@socketio.on("disconnect")
def test_disconnect():
    print(request.sid + " disconnected")


@socketio.on("tileClicked")
def tileClicked(data):
    row, col = data
    notation = chr(col + ord("a")) + str(8 - row)

    room = player_rooms[request.sid]

    moves = room.board.get_available_moves(notation)
    emit("tileClicked", [move.to_dict() for move in moves], to=room.id)


@socketio.on("movePiece")
def movePiece(data):
    start = Position(data["from"][0], data["from"][1])
    end = Position(data["to"][0], data["to"][1])

    room = player_rooms[request.sid]

    room.board.move(start, end)
    emit("board", {"squares": room.board.get_squares()}, to=room.id)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0")
