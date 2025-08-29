import React, { CSSProperties } from "react";
import { Piece } from "./Piece";
import { Square } from "./Square";

const BOARD_SQUARE_PERCENT = 12.5;

export const Tile = React.memo(function Tile({
  type,
  color,
  x,
  y,
  isActive,
  isPossibleMove,
  isPlayerTurn,
  isCheck,
  playerColor,
  onPieceDrop,
  isPremove,
  boardDimensions,
  gameStatus,
  isLastMove,
}: {
  type?: string;
  color?: string;
  x: number;
  y: number;
  isActive: boolean;
  isPossibleMove?: boolean;
  isPlayerTurn?: boolean;
  isCheck?: boolean;
  playerColor: string;
  onPieceDrop?: (x: number, y: number) => void;
  isPremove?: boolean;
  boardDimensions: { width: number; height: number };
  gameStatus?: string;
  isLastMove?: boolean;
}) {
  const pieceStyle: CSSProperties = {
    position: "absolute",
    top: BOARD_SQUARE_PERCENT * x + "%",
    left: BOARD_SQUARE_PERCENT * y + "%",
    width: BOARD_SQUARE_PERCENT + "%",
    height: BOARD_SQUARE_PERCENT + "%",
  };

  return (
    <>
      <div>
        <Square
          light={(x + y) % 2 === 0}
          style={pieceStyle}
          premove={isPremove}
          key={`square-${x}-${y}`}
        ></Square>
        {isCheck && (
          <div
            style={{
              ...pieceStyle,
              background:
                "radial-gradient(ellipse at center, rgb(255, 0, 0) 0%, rgb(231, 0, 0) 25%, rgba(169, 0, 0, 0) 89%, rgba(158, 0, 0, 0) 100%)",
              borderRadius: "50%",
            }}
          ></div>
        )}
        {isActive && (
          <div
            style={{ ...pieceStyle, backgroundColor: "rgba(20, 85, 30, .5)" }}
          ></div>
        )}
        {isLastMove && (
          <div
            style={{ ...pieceStyle, backgroundColor: "rgba(155, 199, 0, .41)" }}
          ></div>
        )}
        <Piece
          type={type}
          color={color}
          style={pieceStyle}
          playerColor={playerColor}
          onPieceDrop={onPieceDrop}
          boardDimensions={boardDimensions}
          gameStatus={gameStatus}
          key={`piece-${x}-${y}`}
        />
      </div>
      {isPossibleMove &&
        (type == null && color == null ? (
          <div
            style={{
              ...pieceStyle,
              background: isPlayerTurn
                ? "radial-gradient(rgba(20, 85, 30, 0.5) 19%, rgba(0, 0, 0, 0) 20%)"
                : "radial-gradient(rgba(20, 30, 85, 0.5) 19%, rgba(0, 0, 0, 0) 20%)",
            }}
          ></div>
        ) : (
          <div
            style={{
              ...pieceStyle,
              background: isPlayerTurn
                ? "radial-gradient(transparent 0%, transparent 79%, rgba(20, 85, 0, 0.3) 80%)"
                : "radial-gradient(transparent 0%, transparent 79%, rgba(20, 30, 85, 0.3) 80%)",
            }}
          ></div>
        ))}
    </>
  );
});
