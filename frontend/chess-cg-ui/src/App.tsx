import { useState, useEffect } from "react";
import { socket } from "./socket";
import { BoardEvent, ChessGame } from "./obj/ChessGame";
import { Board } from "./components/Board";
import { Timer } from "./components/Timer";

export default function App() {
  const [isConnected, setIsConnected] = useState(socket.connected);
  const [chessGame, setChessGame] = useState<ChessGame>(new ChessGame());
  const playerColor =
    chessGame.players?.white === socket.id ? "white" : "black";

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
        time: data.time,
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
    <div
      className="App"
      key="app"
      style={{
        display: "flex",
        gap: "20px",
        padding: "20px",
        margin: 0,
      }}
    >
      {isConnected && (
        <Board
          game={chessGame}
          updatePossibleMoves={updatePossibleMoves}
          key="board"
        />
      )}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "20px",
          justifyContent: "center",
        }}
      >
        <Timer
          initialTime={
            playerColor === "white"
              ? chessGame.time?.black || 0
              : chessGame.time?.white || 0
          }
          isActive={
            chessGame.turn !== playerColor && chessGame.status === "in progress"
          }
        />
        <Timer
          initialTime={
            playerColor === "white"
              ? chessGame.time?.white || 0
              : chessGame.time?.black || 0
          }
          isActive={
            chessGame.turn === playerColor && chessGame.status === "in progress"
          }
        />
      </div>
    </div>
  );
}
