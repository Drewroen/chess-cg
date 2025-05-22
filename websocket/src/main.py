#!/usr/bin/env python3

from obj.objects import Position

from flask import Flask, request
from flask_socketio import SocketIO, emit

from svc.room import RoomService

app = Flask(__name__)
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*", allow_eio3=True)
room_service = RoomService()


@socketio.on("connect")
def test_connect():
    room_id = room_service.add(request.sid)
    print(request.sid + " connected to room " + str(room_id))
    emit(
        "game",
        {
            "squares": room_service.get_room(room_id).game.board.get_squares(),
            "turn": room_service.get_room(room_id).game.turn,
            "players": {
                "white": room_service.get_room(room_id).white,
                "black": room_service.get_room(room_id).black,
            },
            "kings_in_check": room_service.get_room(
                room_id
            ).game.board.kings_in_check(),
        },
        to=room_id,
    )


@socketio.on("disconnect")
def test_disconnect():
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

    room = room_service.get_player_room(request.sid)

    room.game.move(start, end)
    emit(
        "game",
        {
            "squares": room_service.get_room(room.id).game.board.get_squares(),
            "turn": room_service.get_room(room.id).game.turn,
            "players": {
                "white": room_service.get_room(room.id).white,
                "black": room_service.get_room(room.id).black,
            },
            "kings_in_check": room_service.get_room(
                room.id
            ).game.board.kings_in_check(),
        },
        to=room.id,
    )


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0")
