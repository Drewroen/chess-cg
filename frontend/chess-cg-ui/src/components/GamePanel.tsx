import { ChessGame } from "../obj/ChessGame";
import { Timer } from "./Timer";
import { ConnectionStatus } from "./ConnectionStatus";

interface GamePanelProps {
  game: ChessGame;
  playerColor: string;
  isMobile: boolean;
}

export function GamePanel({ game, playerColor, isMobile }: GamePanelProps) {
  // Determine opponent and current player info
  const opponentInfo =
    playerColor === "white"
      ? {
          connected: game.players?.black?.connected || false,
          name: game.players?.black?.name,
          elo: game.players?.black?.elo,
          color: "black" as const,
          time: game.time?.black || 0,
        }
      : {
          connected: game.players?.white?.connected || false,
          name: game.players?.white?.name,
          elo: game.players?.white?.elo,
          color: "white" as const,
          time: game.time?.white || 0,
        };

  const currentPlayerInfo =
    playerColor === "white"
      ? {
          connected: game.players?.white?.connected || false,
          name: game.players?.white?.name,
          elo: game.players?.white?.elo,
          color: "white" as const,
          time: game.time?.white || 0,
        }
      : {
          connected: game.players?.black?.connected || false,
          name: game.players?.black?.name,
          elo: game.players?.black?.elo,
          color: "black" as const,
          time: game.time?.black || 0,
        };

  if (isMobile) {
    return (
      <div
        style={{
          width: "100%",
          display: "flex",
          flexDirection: "column",
          gap: "16px",
          padding: "20px",
          backgroundColor: "#2b2927",
          borderRadius: "8px",
          height: "fit-content",
        }}
      >
        {/* Opponent Info */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "8px",
            padding: "16px",
            backgroundColor: "#3c3a37",
            borderRadius: "6px",
          }}
        >
          <ConnectionStatus
            connected={opponentInfo.connected}
            username={opponentInfo.name}
            elo={opponentInfo.elo}
            playerColor={opponentInfo.color}
            gameStatus={game.status}
            winner={game.winner}
          />
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

        {/* Game Controls */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "8px",
          }}
        >
          <button
            style={{
              padding: "12px 16px",
              backgroundColor: "#f44336",
              color: "white",
              border: "none",
              borderRadius: "6px",
              cursor: "pointer",
              fontSize: "14px",
              fontWeight: "500",
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.backgroundColor = "#d32f2f";
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.backgroundColor = "#f44336";
            }}
          >
            Resign
          </button>
          <button
            style={{
              padding: "12px 16px",
              backgroundColor: "#757575",
              color: "white",
              border: "none",
              borderRadius: "6px",
              cursor: "pointer",
              fontSize: "14px",
              fontWeight: "500",
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.backgroundColor = "#616161";
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.backgroundColor = "#757575";
            }}
          >
            Offer Draw
          </button>
        </div>

        {/* Current Player Info */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "8px",
            padding: "16px",
            backgroundColor: "#3c3a37",
            borderRadius: "6px",
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
          <ConnectionStatus
            connected={currentPlayerInfo.connected}
            username={currentPlayerInfo.name}
            elo={currentPlayerInfo.elo}
            playerColor={currentPlayerInfo.color}
            gameStatus={game.status}
            winner={game.winner}
          />
        </div>
      </div>
    );
  }

  // Non-mobile horizontal layout matching the image design
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
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          gap: "8px",
          padding: "16px 0",
        }}
      >
        <button
          style={{
            padding: "8px 16px",
            backgroundColor: "transparent",
            color: "#888",
            border: "1px solid #555",
            borderRadius: "6px",
            cursor: "pointer",
            fontSize: "14px",
            display: "flex",
            alignItems: "center",
            gap: "4px",
          }}
          title="Offer draw"
        >
          ½
        </button>
        <button
          style={{
            padding: "8px 16px",
            backgroundColor: "transparent",
            color: "#888",
            border: "1px solid #555",
            borderRadius: "6px",
            cursor: "pointer",
            fontSize: "14px",
            display: "flex",
            alignItems: "center",
            gap: "4px",
          }}
          title="Resign"
        >
          ⚐
        </button>
      </div>

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
