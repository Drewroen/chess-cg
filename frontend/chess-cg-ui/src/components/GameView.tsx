import { useState, useEffect, useRef } from "react";
import { BoardEvent, ChessGame } from "../obj/ChessGame";
import { Board } from "./Board";
import { Timer } from "./Timer";

export function GameView() {
  const [chessGame, setChessGame] = useState<ChessGame>(new ChessGame());
  const [connectionStatus, setConnectionStatus] =
    useState<string>("Connecting...");
  const playerColor =
    chessGame.players?.white === chessGame.id ? "white" : "black";

  function updatePossibleMoves(moves: Array<[number, number]>) {
    setChessGame((prevGame) => ({ ...prevGame, possibleMoves: moves }));
  }

  const connection = useRef(null as WebSocket | null);

  useEffect(() => {
    function onGame(data: BoardEvent) {
      console.log("Processing game data:", data);
      setChessGame((prevGame) => {
        const newGame = {
          ...prevGame,
          board: { squares: data.squares },
          turn: data.turn,
          players: data.players,
          kingsInCheck: data.kings_in_check,
          status: data.status,
          time: data.time,
          moves: data.moves,
          id: data.id,
        };
        console.log("Updated game state:", newGame);
        return newGame;
      });
    }

    if (connection.current) {
      console.log("WebSocket already connected");
      return;
    }

    const socket = new WebSocket("ws://127.0.0.1:8000/ws");

    socket.addEventListener("message", (event) => {
      const data = JSON.parse(event.data);
      console.log("Received WebSocket data:", data);
      onGame(data);
    });

    socket.addEventListener("open", () => {
      console.log("WebSocket connected");
      setConnectionStatus("Connected");
    });

    socket.addEventListener("error", (error) => {
      console.error("WebSocket error:", error);
      setConnectionStatus("Error");
    });

    socket.addEventListener("close", () => {
      console.log("WebSocket disconnected");
      setConnectionStatus("Disconnected");
    });

    connection.current = socket;

    return () => {
      if (connection.current?.readyState === WebSocket.OPEN) {
        connection.current.close();
      }
    };
  }, []); // Remove chessGame dependency to prevent reconnection loop

  return (
    <div
      style={{
        display: "flex",
        gap: "20px",
        padding: "20px",
        margin: 0,
        minHeight: "100vh",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          position: "absolute",
          top: "10px",
          right: "10px",
          padding: "10px",
          background: "lightgray",
          borderRadius: "5px",
        }}
      >
        Status: {connectionStatus}
      </div>
      {connection.current && (
        <Board
          game={chessGame}
          updatePossibleMoves={updatePossibleMoves}
          key="board"
          socket={connection.current}
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
