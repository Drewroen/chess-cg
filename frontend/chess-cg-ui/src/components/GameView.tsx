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

// Custom hook for responsive design
function useResponsive() {
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return isMobile;
}

// Custom hook for auth token management
function useAuthToken() {
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAuthToken = async () => {
      try {
        setIsLoading(true);
        setError(null);

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
        } else {
          setError("Failed to fetch auth token");
        }
      } catch (err) {
        setError("Could not fetch access token");
        console.error("Could not fetch access token:", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAuthToken();
  }, []);

  return { authToken, isLoading, error };
}

// Custom hook for WebSocket connection
function useWebSocket(onMessage: (data: BoardEvent) => void) {
  const [connectionStatus, setConnectionStatus] =
    useState<ConnectionStatusType>("connecting");
  const socketRef = useRef<WebSocket | null>(null);
  const onMessageRef = useRef(onMessage);
  const { authToken, isLoading: authLoading } = useAuthToken();

  // Keep the latest onMessage callback in a ref
  useEffect(() => {
    onMessageRef.current = onMessage;
  }, [onMessage]);

  useEffect(() => {
    // Wait for auth token to be loaded
    if (authLoading) return;

    // Only connect if we don't already have an active connection
    if (
      socketRef.current &&
      socketRef.current.readyState !== WebSocket.CLOSED
    ) {
      return;
    }

    const connect = async () => {
      let wsUrl = WEBSOCKET_URL;

      // Add token to URL if available
      if (authToken) {
        wsUrl = `${WEBSOCKET_URL}?token=${encodeURIComponent(authToken)}`;
      }

      const socket = new WebSocket(wsUrl);

      socket.addEventListener("message", (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessageRef.current(data);
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
        socketRef.current = null;
      });

      socketRef.current = socket;
    };

    connect();

    return () => {
      if (
        socketRef.current &&
        socketRef.current.readyState === WebSocket.OPEN
      ) {
        socketRef.current.close();
      }
      socketRef.current = null;
    };
  }, [authToken, authLoading]); // Re-connect when auth token changes

  return { socket: socketRef.current, connectionStatus };
}

export function GameView() {
  const [chessGame, setChessGame] = useState<ChessGame>(new ChessGame());
  const isMobile = useResponsive();

  const updateGameState = useCallback((data: BoardEvent) => {
    setChessGame((prevGame) => ({
      ...prevGame,
      board: { squares: data.squares },
      turn: data.turn,
      players: data.players,
      kingsInCheck: data.kings_in_check,
      status: data.status,
      winner: data.winner,
      time: data.time,
      moves: data.moves,
      premoves: data.premoves,
      id: data.id,
    }));
  }, []);

  const { socket, connectionStatus } = useWebSocket(updateGameState);

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
        flexDirection: isMobile ? "column" : "row",
        gap: "20px",
        padding: "20px",
        margin: 0,
        minHeight: "100vh",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {process.env.NODE_ENV === "development" && (
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
      )}
      {chessGame.board?.squares ? (
        <>
          {/* Top timer for mobile layout */}
          {isMobile && (
            <div
              style={{
                display: "flex",
                flexDirection: "row",
                alignItems: "center",
                gap: "6px",
              }}
            >
              <ConnectionStatus
                connected={
                  playerColor === "white"
                    ? chessGame.players?.black?.connected || false
                    : chessGame.players?.white?.connected || false
                }
                username={
                  playerColor === "white"
                    ? chessGame.players?.black?.name
                    : chessGame.players?.white?.name
                }
                elo={
                  playerColor === "white"
                    ? chessGame.players?.black?.elo
                    : chessGame.players?.white?.elo
                }
                playerColor={playerColor === "white" ? "black" : "white"}
                gameStatus={chessGame.status}
                winner={chessGame.winner}
              />
              <Timer
                initialTime={
                  chessGame.status === "not started" 
                    ? 10
                    : (playerColor === "white"
                        ? chessGame.time?.black || 0
                        : chessGame.time?.white || 0)
                }
                isActive={
                  chessGame.status === "not started" 
                    ? chessGame.turn !== playerColor
                    : (chessGame.turn !== playerColor &&
                       chessGame.status === "in progress")
                }
                isMobile={isMobile}
              />
            </div>
          )}

          {socket && (
            <Board
              game={chessGame}
              updatePossibleMoves={updatePossibleMoves}
              key="board"
              socket={socket}
            />
          )}

          {/* Bottom timer for mobile layout or side timers for desktop */}
          {isMobile ? (
            <div
              style={{
                display: "flex",
                flexDirection: "row",
                alignItems: "center",
                gap: "6px",
              }}
            >
              <ConnectionStatus
                connected={
                  playerColor === "white"
                    ? chessGame.players?.white?.connected || false
                    : chessGame.players?.black?.connected || false
                }
                username={
                  playerColor === "white"
                    ? chessGame.players?.white?.name
                    : chessGame.players?.black?.name
                }
                elo={
                  playerColor === "white"
                    ? chessGame.players?.white?.elo
                    : chessGame.players?.black?.elo
                }
                playerColor={playerColor}
                gameStatus={chessGame.status}
                winner={chessGame.winner}
              />
              <Timer
                initialTime={
                  chessGame.status === "not started" 
                    ? 10
                    : (playerColor === "white"
                        ? chessGame.time?.white || 0
                        : chessGame.time?.black || 0)
                }
                isActive={
                  chessGame.status === "not started" 
                    ? chessGame.turn === playerColor
                    : (chessGame.turn === playerColor &&
                       chessGame.status === "in progress")
                }
                isMobile={isMobile}
              />
            </div>
          ) : (
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "6px",
                justifyContent: "center",
              }}
            >
              <ConnectionStatus
                connected={
                  playerColor === "white"
                    ? chessGame.players?.black?.connected || false
                    : chessGame.players?.white?.connected || false
                }
                username={
                  playerColor === "white"
                    ? chessGame.players?.black?.name
                    : chessGame.players?.white?.name
                }
                elo={
                  playerColor === "white"
                    ? chessGame.players?.black?.elo
                    : chessGame.players?.white?.elo
                }
                playerColor={playerColor === "white" ? "black" : "white"}
                gameStatus={chessGame.status}
                winner={chessGame.winner}
              />
              <Timer
                initialTime={
                  chessGame.status === "not started" 
                    ? 10
                    : (playerColor === "white"
                        ? chessGame.time?.black || 0
                        : chessGame.time?.white || 0)
                }
                isActive={
                  chessGame.status === "not started" 
                    ? chessGame.turn !== playerColor
                    : (chessGame.turn !== playerColor &&
                       chessGame.status === "in progress")
                }
                isMobile={isMobile}
              />
              <div style={{ height: 20 }}></div>
              <Timer
                initialTime={
                  chessGame.status === "not started" 
                    ? 10
                    : (playerColor === "white"
                        ? chessGame.time?.white || 0
                        : chessGame.time?.black || 0)
                }
                isActive={
                  chessGame.status === "not started" 
                    ? chessGame.turn === playerColor
                    : (chessGame.turn === playerColor &&
                       chessGame.status === "in progress")
                }
                isMobile={isMobile}
              />
              <ConnectionStatus
                connected={
                  playerColor === "white"
                    ? chessGame.players?.white?.connected || false
                    : chessGame.players?.black?.connected || false
                }
                username={
                  playerColor === "white"
                    ? chessGame.players?.white?.name
                    : chessGame.players?.black?.name
                }
                elo={
                  playerColor === "white"
                    ? chessGame.players?.white?.elo
                    : chessGame.players?.black?.elo
                }
                playerColor={playerColor}
                gameStatus={chessGame.status}
                winner={chessGame.winner}
              />
            </div>
          )}
        </>
      ) : (
        <div>Loading...</div>
      )}
    </div>
  );
}
