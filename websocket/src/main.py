#!/usr/bin/env python3

from obj.objects import Position

from flask import Flask, request
from flask_socketio import SocketIO, emit

from svc.room import RoomService

app = Flask(__name__)
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*", allow_eio3=True)
room_service = RoomService()


def emit_game_state(room_id):
    """Emit the current game state to all players in the room."""
    room = room_service.get_room(room_id)
    emit(
        "game",
        {
            "squares": room.game.board.get_squares(),
            "turn": room.game.turn,
            "players": {
                "white": room.white,
                "black": room.black,
            },
            "kings_in_check": room.game.board.kings_in_check(),
            "status": room.game.status.value,
            "time": {
                "white": room.game.white_time_left,
                "black": room.game.black_time_left,
            },
        },
        to=room_id,
    )


@socketio.on("connect")
def connect():
    room_id = room_service.add(request.sid)
    print(request.sid + " connected to room " + str(room_id))
    emit_game_state(room_id)


@socketio.on("disconnect")
def disconnect():
    print(request.sid + " disconnected")


@socketio.on("tileClicked")
def tileClicked(data):
    row, col = data

    room = room_service.get_player_room(request.sid)

    moves = room.game.board.get_available_moves(Position(row, col))
    emit("tileClicked", [move.to_dict() for move in moves], to=request.sid)


@socketio.on("movePiece")
def movePiece(data):
    start = Position(data["from"][0], data["from"][1])
    end = Position(data["to"][0], data["to"][1])
    promote_to = data.get("promotion", None)

    room = room_service.get_player_room(request.sid)

    room.game.move(start, end, promote_to)
    emit_game_state(room.id)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0")
