import { useState, useEffect, useRef, useCallback } from "react";
import { BoardEvent, ChessGame } from "../obj/ChessGame";
import { Board } from "./Board";
import { Timer } from "./Timer";

type ConnectionStatus = "connecting" | "connected" | "disconnected" | "error";

const WEBSOCKET_URL = "ws://127.0.0.1:8000/ws";

// Custom hook for WebSocket connection
function useWebSocket(onMessage: (data: BoardEvent) => void) {
  const [connectionStatus, setConnectionStatus] =
    useState<ConnectionStatus>("connecting");
  const socketRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    if (socketRef.current) return;

    const socket = new WebSocket(WEBSOCKET_URL);

    socket.addEventListener("message", (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log("Received WebSocket data:", data);
        onMessage(data);
      } catch (error) {
        console.error("Failed to parse WebSocket message:", error);
      }
    });

    socket.addEventListener("open", () => {
      console.log("WebSocket connected");
      setConnectionStatus("connected");
    });

    socket.addEventListener("error", (error) => {
      console.error("WebSocket error:", error);
      setConnectionStatus("error");
    });

    socket.addEventListener("close", () => {
      console.log("WebSocket disconnected");
      setConnectionStatus("disconnected");
    });

    socketRef.current = socket;
  }, [onMessage]);

  useEffect(() => {
    connect();

    return () => {
      if (socketRef.current?.readyState === WebSocket.OPEN) {
        socketRef.current.close();
      }
    };
  }, [connect]);

  return { socket: socketRef.current, connectionStatus };
}

export function GameView() {
  const [chessGame, setChessGame] = useState<ChessGame>(new ChessGame());

  const updateGameState = useCallback((data: BoardEvent) => {
    setChessGame((prevGame) => ({
      ...prevGame,
      board: { squares: data.squares },
      turn: data.turn,
      players: data.players,
      kingsInCheck: data.kings_in_check,
      status: data.status,
      time: data.time,
      moves: data.moves,
      id: data.id,
    }));
  }, []);

  const { socket, connectionStatus } = useWebSocket(updateGameState);

  const playerColor =
    chessGame.players?.white === chessGame.id ? "white" : "black";

  const updatePossibleMoves = useCallback((moves: Array<[number, number]>) => {
    setChessGame((prevGame) => ({ ...prevGame, possibleMoves: moves }));
  }, []);

  const getStatusDisplay = (status: ConnectionStatus) => {
    const statusMap = {
      connecting: "Connecting...",
      connected: "Connected",
      disconnected: "Disconnected",
      error: "Error",
    };
    return statusMap[status];
  };

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
        Status: {getStatusDisplay(connectionStatus)}
      </div>
      {socket && (
        <Board
          game={chessGame}
          updatePossibleMoves={updatePossibleMoves}
          key="board"
          socket={socket}
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
