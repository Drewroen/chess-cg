#!/usr/bin/env python3

import obj.chess as chess
from obj.objects import Piece, Position

from flask import Flask, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*", allow_eio3=True)


board = chess.Board()


@socketio.on("connect")
def test_connect():
    print(request.sid + " connected")
    emit("board", {"squares": board.get_squares()}, broadcast=True)


@socketio.on("disconnect")
def test_disconnect():
    print(request.sid + " disconnected")


@socketio.on("tileClicked")
def tileClicked(data):
    row, col = data
    notation = chr(col + ord("a")) + str(8 - row)
    moves = board.get_available_moves(notation)
    emit("tileClicked", [move.to_dict() for move in moves], broadcast=True)


@socketio.on("movePiece")
def movePiece(data):
    start = Position(data["from"][0], data["from"][1])
    end = Position(data["to"][0], data["to"][1])
    board.move(start, end)
    emit("board", {"squares": board.get_squares()}, broadcast=True)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0")
