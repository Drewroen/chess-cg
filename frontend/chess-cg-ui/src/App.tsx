import { useState, useEffect } from "react";
import { socket } from "./socket";
import { ChessBoard, ChessGame } from "./obj/ChessGame";
import { Board } from "./components/Board";

export default function App() {
  const [isConnected, setIsConnected] = useState(socket.connected);
  const [chessGame, setChessGame] = useState<ChessGame>(new ChessGame());

  function updatePossibleMoves(moves: Array<[number, number]>) {
    setChessGame({ ...chessGame, possibleMoves: moves });
  }

  useEffect(() => {
    function onConnect() {
      setIsConnected(true);
    }

    function onDisconnect() {
      setIsConnected(false);
      setChessGame(new ChessGame());
    }

    function onBoard(data: ChessBoard) {
      setChessGame({ ...chessGame, board: data });
    }

    function onTileClick(data: any) {
      const moves: Array<[number, number]> = data.map((move: any) => {
        const position = move.position_to_move;
        return [position.row, position.col];
      });
      setChessGame({ ...chessGame, possibleMoves: moves });
    }

    socket.on("connect", onConnect);
    socket.on("disconnect", onDisconnect);
    socket.on("board", onBoard);
    socket.on("tileClicked", onTileClick);

    return () => {
      socket.off("connect");
      socket.off("disconnect");
      socket.off("board");
      socket.off("tileClicked");
    };
  }, [chessGame]);

  console.log(chessGame);
  return (
    <div className="App" key="app">
      {isConnected && (
        <Board
          game={chessGame}
          updatePossibleMoves={updatePossibleMoves}
          key="board"
        />
      )}
    </div>
  );
}
