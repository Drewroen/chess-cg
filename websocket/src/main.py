#!/usr/bin/env python3

import obj.chess as chess

from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)

if __name__ == "__main__":
    board = chess.Board()
    board.reset_board()
    board.move("a2", "a4")
    print(board.get_available_moves("a1"))
    board.move("a1", "a3")
    print(board.get_available_moves("b1"))
    board.move("b1", "c3")
    print(board.get_available_moves("c3"))
    board.move("d2", "d4")
    print(board.get_available_moves("c1"))
    board.move("c1", "f4")
    print(board.get_available_moves("f4"))
    board.move("f4", "e5")
    print(board.get_available_moves("e5"))

    board.print_board()
    socketio.run(app, host="0.0.0.0")
