import { useState, useEffect, useRef, useCallback } from "react";
import { BoardEvent, ChessGame } from "../obj/ChessGame";
import { Board } from "./Board";
import { Timer } from "./Timer";
import { ConnectionStatus } from "./ConnectionStatus";

type ConnectionStatusType =
  | "connecting"
  | "connected"
  | "disconnected"
  | "error";

const WEBSOCKET_URL = "ws://127.0.0.1:8000/ws";
const BACKEND_URL =
  process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";

// Custom hook for WebSocket connection
function useWebSocket(
  onMessage: (data: BoardEvent) => void,
  authToken: string | null
) {
  const [connectionStatus, setConnectionStatus] =
    useState<ConnectionStatusType>("connecting");
  const socketRef = useRef<WebSocket | null>(null);

  const connect = useCallback(
    (authToken: string | null) => {
      if (socketRef.current) return;
      console.log(authToken);
      if (authToken === null) return;

      // Tokens are now in httpOnly cookies and handled by the browser automatically
      // WebSocket connections will include cookies automatically when using credentials
      const wsUrl = `${WEBSOCKET_URL}?token=${encodeURIComponent(authToken)}`;

      const socket = new WebSocket(wsUrl);

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
        console.debug("WebSocket connected");
        setConnectionStatus("connected");
      });

      socket.addEventListener("error", (error) => {
        console.error("WebSocket error:", error);
        setConnectionStatus("error");
      });

      socket.addEventListener("close", () => {
        console.debug("WebSocket disconnected");
        setConnectionStatus("disconnected");
      });

      socketRef.current = socket;
    },
    [onMessage]
  );

  useEffect(() => {
    connect(authToken);

    return () => {
      if (socketRef.current?.readyState === WebSocket.OPEN) {
        socketRef.current.close();
      }
    };
  }, [connect, authToken]);

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

  const [authToken, setAuthToken] = useState<string | null>(null);

  useEffect(() => {
    const fetchAuthToken = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/auth/ws-token`, {
          method: "GET",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (response.ok) {
          const { access_token } = await response.json();
          setAuthToken(access_token);
        }
      } catch (error) {
        console.log("Could not fetch access token:", error);
      }
    };

    fetchAuthToken();
  }, []);

  const { socket, connectionStatus } = useWebSocket(updateGameState, authToken);

  const playerColor =
    chessGame.players?.white.id === chessGame.id ? "white" : "black";

  const updatePossibleMoves = useCallback((moves: Array<[number, number]>) => {
    setChessGame((prevGame) => ({ ...prevGame, possibleMoves: moves }));
  }, []);

  const getStatusDisplay = (status: ConnectionStatusType) => {
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
      {chessGame.board?.squares ? (
        <>
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
              gap: "6px",
              justifyContent: "center",
            }}
          >
            <ConnectionStatus
              connected={chessGame.players?.white?.connected || false}
              username={chessGame.players?.white?.name}
            />
            <Timer
              initialTime={
                playerColor === "white"
                  ? chessGame.time?.black || 0
                  : chessGame.time?.white || 0
              }
              isActive={
                chessGame.turn !== playerColor &&
                chessGame.status === "in progress"
              }
            />
            <div style={{ height: 20 }}></div>
            <Timer
              initialTime={
                playerColor === "white"
                  ? chessGame.time?.white || 0
                  : chessGame.time?.black || 0
              }
              isActive={
                chessGame.turn === playerColor &&
                chessGame.status === "in progress"
              }
            />
            <ConnectionStatus
              connected={chessGame.players?.black?.connected || false}
              username={chessGame.players?.black?.name}
            />
          </div>
        </>
      ) : (
        <div>Loading...</div>
      )}
    </div>
  );
}
