import { ChessGame } from "../obj/ChessGame";
import { Timer } from "./Timer";
import { GameInfo } from "../services/gameService";
import { DrawResignButtons } from "./DrawResignButtons";
import { GameOver } from "./GameOver";

interface GamePanelProps {
  game: ChessGame;
  gameInfo: GameInfo | null;
  playerColor: string;
  socket?: WebSocket | null;
}

export function GamePanel({ game, gameInfo, playerColor, socket }: GamePanelProps) {
  // Determine opponent and current player info
  const opponentInfo =
    playerColor === "white"
      ? {
          connected: game.opponentConnected,
          name: gameInfo?.players.black?.name || "Opponent",
          elo: gameInfo?.players.black?.elo,
          color: "black" as const,
          time: game.time?.black || 0,
        }
      : {
          connected: game.opponentConnected,
          name: gameInfo?.players.white?.name || "Opponent",
          elo: gameInfo?.players.white?.elo,
          color: "white" as const,
          time: game.time?.white || 0,
        };

  const currentPlayerInfo =
    playerColor === "white"
      ? {
          connected: true, // Player is always connected (it's us)
          name: gameInfo?.players.white?.name || "You",
          elo: gameInfo?.players.white?.elo,
          color: "white" as const,
          time: game.time?.white || 0,
        }
      : {
          connected: true, // Player is always connected (it's us)
          name: gameInfo?.players.black?.name || "You",
          elo: gameInfo?.players.black?.elo,
          color: "black" as const,
          time: game.time?.black || 0,
        };

  // Desktop layout
  return (
    <div
      style={{
        width: "350px",
        display: "flex",
        flexDirection: "column",
        padding: "16px",
        backgroundColor: "#2b2927",
        borderRadius: "8px",
        height: "fit-content",
        gap: "4px",
      }}
    >
      {/* Opponent Timer - Top */}
      <div
        style={{
          display: "flex",
          justifyContent: "flex-start",
          alignItems: "center",
        }}
      >
        <Timer
          initialTime={game.status === "not started" ? 10 : opponentInfo.time}
          isActive={
            game.status === "not started"
              ? game.turn !== playerColor
              : game.turn !== playerColor && game.status === "in progress"
          }
          isMobile={false}
        />
      </div>

      {/* Opponent Info - Below Timer */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "8px",
          justifyContent: "space-between",
          paddingBottom: "8px",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
          }}
        >
          <div
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              backgroundColor: opponentInfo.connected ? "#22c55e" : "#6b7280",
              flexShrink: 0,
            }}
          />
          <span
            style={{
              color: "white",
              fontWeight: 100,
              fontFamily: "sans-serif",
              fontSize: "18px",
            }}
          >
            {opponentInfo.name?.startsWith("Guest_")
              ? "Guest"
              : opponentInfo.name}
          </span>
        </div>
        {opponentInfo.elo && (
          <span
            style={{
              color: "white",
              fontWeight: 100,
              fontFamily: "sans-serif",
              fontSize: "18px",
            }}
          >
            {opponentInfo.elo}
          </span>
        )}
      </div>

      {/* Game Controls - Center */}
      <DrawResignButtons 
        socket={socket} 
        drawRequests={game.drawRequests}
        playerColor={playerColor as "white" | "black"}
      />

      {/* Game Over message */}
      {(game.status === "complete" || game.status === "aborted") && (
        <GameOver winner={game.winner} endReason={game.endReason} />
      )}

      {/* Current Player Info - Above Timer */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "8px",
          justifyContent: "space-between",
          paddingTop: "8px",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
          }}
        >
          <div
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              backgroundColor: currentPlayerInfo.connected
                ? "#22c55e"
                : "#6b7280",
              flexShrink: 0,
            }}
          />
          <span
            style={{
              color: "white",
              fontWeight: 100,
              fontFamily: "sans-serif",
              fontSize: "18px",
            }}
          >
            {currentPlayerInfo.name?.startsWith("Guest_")
              ? "Guest"
              : currentPlayerInfo.name}
          </span>
        </div>
        {currentPlayerInfo.elo && (
          <span
            style={{
              color: "white",
              fontWeight: 100,
              fontFamily: "sans-serif",
              fontSize: "18px",
            }}
          >
            {currentPlayerInfo.elo}
          </span>
        )}
      </div>

      {/* Current Player Timer - Bottom */}
      <div
        style={{
          display: "flex",
          justifyContent: "flex-start",
          alignItems: "center",
        }}
      >
        <Timer
          initialTime={
            game.status === "not started" ? 10 : currentPlayerInfo.time
          }
          isActive={
            game.status === "not started"
              ? game.turn === playerColor
              : game.turn === playerColor && game.status === "in progress"
          }
          isMobile={false}
        />
      </div>
    </div>
  );
}
