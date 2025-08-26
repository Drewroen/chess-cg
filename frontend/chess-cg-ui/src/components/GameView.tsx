import { useState, useEffect, useRef, useCallback } from "react";
import { BoardEvent, ChessGame, ChessPiece } from "../obj/ChessGame";
import { Board } from "./Board";
import { Timer } from "./Timer";
import { GamePanel } from "./GamePanel";
import { DrawResignButtons } from "./DrawResignButtons";
import { GameOver } from "./GameOver";
import { fetchGameInfo, GameInfo } from "../services/gameService";
import styles from "./GameView.module.css";
import utilities from "../styles/utilities.module.css";

type ConnectionStatusType =
  | "connecting"
  | "connected"
  | "disconnected"
  | "error";

const WEBSOCKET_URL =
  process.env.REACT_APP_WEBSOCKET_URL || "ws://127.0.0.1:8000/ws";
const BACKEND_URL =
  process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";


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

export function GameView({ isMobile }: { isMobile: boolean }) {
  const [chessGame, setChessGame] = useState<ChessGame>(new ChessGame());
  const [gameInfo, setGameInfo] = useState<GameInfo | null>(null);

  const updateGameState = useCallback((data: BoardEvent) => {
    setChessGame((prevGame) => ({
      ...prevGame,
      board: { squares: data.squares },
      turn: data.turn,
      kingsInCheck: data.kings_in_check,
      status: data.status,
      winner: data.winner,
      endReason: data.end_reason,
      time: data.time,
      moves: data.moves, // Now simplified to single array
      opponentConnected: data.opponent_connected,
      id: data.id, // Room ID
      playerId: data.player_id, // Player ID
      drawRequests: data.draw_requests,
    }));
  }, []);

  // Fetch static game info when we get our first update with room ID
  useEffect(() => {
    if (chessGame.id && !gameInfo) {
      fetchGameInfo(chessGame.id).then(setGameInfo).catch(console.error);
    }
  }, [chessGame.id, gameInfo]);

  const { socket } = useWebSocket(updateGameState);

  const playerColor =
    gameInfo?.players.white.id === chessGame.playerId ? "white" : "black";


  const handleLocalMove = useCallback(
    (from: [number, number], to: [number, number]) => {
      setChessGame((prevGame) => {
        if (!prevGame.board?.squares) return prevGame;

        const newSquares: (ChessPiece | null)[][] = prevGame.board.squares.map(
          (row) => [...row]
        );
        const piece = newSquares[from[0]][from[1]];
        newSquares[from[0]][from[1]] = null;
        newSquares[to[0]][to[1]] = piece;

        return {
          ...prevGame,
          board: { squares: newSquares },
          turn: prevGame.turn === "white" ? "black" : "white",
        };
      });
    },
    []
  );


  return (
    <div className={`${utilities.flexCenter} ${utilities.minHeight100vh} ${utilities.bgDark} ${utilities.margin0} ${isMobile ? styles.gameContainerMobile : styles.gameContainer}`}>
      {chessGame.board?.squares && gameInfo ? (
        <>
          {/* Mobile layout - player info above and below board */}
          {isMobile ? (
            <>
              {/* Opponent info at top */}
              <div className={`${styles.playerInfoContainer} ${styles.opponentInfo}`}>
                <div className={styles.playerDetails}>
                  <div
                    className={`${styles.connectionDot} ${
                      chessGame.opponentConnected ? styles.connected : styles.disconnected
                    }`}
                  />
                  <span className={styles.playerName}>
                    {playerColor === "white"
                      ? gameInfo?.players.black.name || "Opponent"
                      : gameInfo?.players.white.name || "Opponent"}
                  </span>
                  <span className={styles.playerElo}>
                    {playerColor === "white"
                      ? gameInfo?.players.black.elo || ""
                      : gameInfo?.players.white.elo || ""}
                  </span>
                </div>
                <Timer
                  initialTime={
                    chessGame.status === "not started"
                      ? 10
                      : playerColor === "white"
                      ? chessGame.time?.black || 0
                      : chessGame.time?.white || 0
                  }
                  isActive={
                    chessGame.status === "not started"
                      ? chessGame.turn !== playerColor
                      : chessGame.turn !== playerColor &&
                        chessGame.status === "in progress"
                  }
                  isMobile={true}
                />
              </div>

              {/* Chess board */}
              {socket && (
                <Board
                  game={chessGame}
                  key="board"
                  socket={socket}
                  onMoveLocal={handleLocalMove}
                  playerColor={playerColor}
                />
              )}

              {/* Current player timer right under the board */}
              <div className={`${styles.playerInfoContainer} ${styles.currentPlayerInfo}`}>
                <div className={styles.playerDetails}>
                  <div className={`${styles.connectionDot} ${styles.connected}`} />
                  <span className={styles.playerName}>
                    {playerColor === "white"
                      ? gameInfo?.players.white.name || "You"
                      : gameInfo?.players.black.name || "You"}
                  </span>
                  <span className={styles.playerElo}>
                    {playerColor === "white"
                      ? gameInfo?.players.white.elo || ""
                      : gameInfo?.players.black.elo || ""}
                  </span>
                </div>
                <Timer
                  initialTime={
                    chessGame.status === "not started"
                      ? 10
                      : playerColor === "white"
                      ? chessGame.time?.white || 0
                      : chessGame.time?.black || 0
                  }
                  isActive={
                    chessGame.status === "not started"
                      ? chessGame.turn === playerColor
                      : chessGame.turn === playerColor &&
                        chessGame.status === "in progress"
                  }
                  isMobile={true}
                />
              </div>

              {/* Game control buttons */}
              <DrawResignButtons
                isMobile={true}
                socket={socket}
                drawRequests={chessGame.drawRequests}
                playerColor={playerColor}
              />

              {/* Game Over message */}
              {(chessGame.status === "complete" ||
                chessGame.status === "aborted") && (
                <GameOver
                  isMobile={true}
                  winner={chessGame.winner}
                  endReason={chessGame.endReason}
                />
              )}
            </>
          ) : (
            /* Desktop layout - board on left, panel on right */
            <>
              {socket && (
                <Board
                  game={chessGame}
                  key="board"
                  socket={socket}
                  onMoveLocal={handleLocalMove}
                  playerColor={playerColor}
                />
              )}
              <GamePanel
                game={chessGame}
                gameInfo={gameInfo}
                playerColor={playerColor}
                socket={socket}
              />
            </>
          )}
        </>
      ) : (
        <div className={styles.loading}>Loading...</div>
      )}
    </div>
  );
}
