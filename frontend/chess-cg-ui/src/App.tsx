import { useState, useEffect } from "react";
import { socket } from "./socket";
import { BoardEvent, ChessGame } from "./obj/ChessGame";
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

    function onGame(data: BoardEvent) {
      setChessGame({
        ...chessGame,
        board: data,
        turn: data.turn,
        players: data.players,
        kingsInCheck: data.kings_in_check,
        status: data.status,
      });
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
    socket.on("game", onGame);
    socket.on("tileClicked", onTileClick);

    return () => {
      socket.off("connect");
      socket.off("disconnect");
      socket.off("game");
      socket.off("tileClicked");
    };
  }, [chessGame]);

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
