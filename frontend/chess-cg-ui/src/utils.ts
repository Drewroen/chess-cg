import { useState, useEffect } from "react";
import { GameInfo } from "./services/gameService";
import { ChessGame, PieceColor } from "./obj/ChessGame";

// ============================================================================
// TIME UTILITIES
// ============================================================================

/**
 * Formats a time value in seconds to a human-readable string.
 *
 * @param seconds - The time in seconds to format
 * @returns Formatted time string in MM:SS or H:MM:SS format
 */
export const formatTime = (seconds: number): string => {
  const total = Math.max(0, seconds);
  const hours = Math.floor(total / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  const secs = total % 60;

  const mm = minutes.toString().padStart(2, "0");
  const ss = secs.toFixed(1).padStart(4, "0");

  return hours > 0 ? `${hours}:${mm}:${ss}` : `${mm}:${ss}`;
};

// ============================================================================
// PLAYER UTILITIES
// ============================================================================

/**
 * Gets the opponent's display information based on player color
 */
export const getOpponentInfo = (
  gameInfo: GameInfo | null,
  playerColor: PieceColor
) => {
  if (!gameInfo) return { name: "Opponent", elo: "" };

  const opponent =
    playerColor === "white" ? gameInfo.players.black : gameInfo.players.white;
  return {
    name: opponent.name || "Opponent",
    elo: opponent.elo || "",
  };
};

/**
 * Gets the current player's display information based on player color
 */
export const getCurrentPlayerInfo = (
  gameInfo: GameInfo | null,
  playerColor: PieceColor
) => {
  if (!gameInfo) return { name: "You", elo: "" };

  const currentPlayer =
    playerColor === "white" ? gameInfo.players.white : gameInfo.players.black;
  return {
    name: currentPlayer.name || "You",
    elo: currentPlayer.elo || "",
  };
};

// ============================================================================
// GAME UTILITIES
// ============================================================================

/**
 * Calculates the initial timer value for a player
 */
export const getTimerInitialTime = (
  chessGame: ChessGame,
  playerColor: PieceColor,
  isOpponent: boolean = false
): number => {
  if (chessGame.status === "not started") {
    return 20;
  }

  const targetColor = isOpponent
    ? playerColor === "white"
      ? "black"
      : "white"
    : playerColor;

  return chessGame.time?.[targetColor as "white" | "black"] || 0;
};

/**
 * Determines if a timer should be active based on game state
 */
export const isTimerActive = (
  chessGame: ChessGame,
  playerColor: PieceColor,
  isOpponent: boolean = false
): boolean => {
  if (chessGame.status === "not started") {
    return isOpponent
      ? chessGame.turn !== playerColor
      : chessGame.turn === playerColor;
  }

  if (chessGame.status !== "in progress") {
    return false;
  }

  return isOpponent
    ? chessGame.turn !== playerColor
    : chessGame.turn === playerColor;
};

// ============================================================================
// BOARD UTILITIES
// ============================================================================

/**
 * Transforms board coordinates based on player perspective
 * White player sees the board normally, black player sees it flipped
 */
export const transformCoordinate = (
  coordinate: number,
  playerColor: PieceColor
): number => {
  return playerColor === "white" ? coordinate : 7 - coordinate;
};

/**
 * Transforms a pair of coordinates [x, y] based on player perspective
 */
export const transformCoordinates = (
  x: number,
  y: number,
  playerColor: PieceColor
): [number, number] => {
  return [
    transformCoordinate(x, playerColor),
    transformCoordinate(y, playerColor),
  ];
};

// ============================================================================
// UI UTILITIES
// ============================================================================

/**
 * Custom hook for responsive design based on window width
 * @param breakpoint - The breakpoint width (default: 768px)
 * @returns boolean indicating if the screen is mobile
 */
export const useResponsive = (breakpoint: number = 768): boolean => {
  const [isMobile, setIsMobile] = useState(window.innerWidth <= breakpoint);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= breakpoint);
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [breakpoint]);

  return isMobile;
};
