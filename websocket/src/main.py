#!/usr/bin/env python3

import obj.chess as chess

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
    print("Client disconnected")


@socketio.on("move")
def move(data):
    start = data["start"]
    end = data["end"]
    board.move(start, end)
    emit("board", {"squares": board.get_squares()}, broadcast=True)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0")
