import BlackKing from "../assets/black_king.svg";
import BlackQueen from "../assets/black_queen.svg";
import BlackRook from "../assets/black_rook.svg";
import BlackBishop from "../assets/black_bishop.svg";
import BlackKnight from "../assets/black_knight.svg";
import BlackPawn from "../assets/black_pawn.svg";
import WhiteKing from "../assets/white_king.svg";
import WhiteQueen from "../assets/white_queen.svg";
import WhiteRook from "../assets/white_rook.svg";
import WhiteBishop from "../assets/white_bishop.svg";
import WhiteKnight from "../assets/white_knight.svg";
import WhitePawn from "../assets/white_pawn.svg";
import React, { CSSProperties, useRef, useState, useEffect } from "react";
import { modifierIcons } from "../utils/modifierIcons";

export const Piece = React.memo(function Piece({
  type,
  color,
  style,
  playerColor,
  onPieceDrop,
  boardDimensions,
  gameStatus,
  modifiers = [],
}: {
  type?: string;
  color?: string;
  style: CSSProperties;
  playerColor: string;
  onPieceDrop?: (x: number, y: number) => void;
  boardDimensions: { width: number; height: number };
  gameStatus?: string;
  modifiers?: (string | { type: string })[];
}) {
  const nodeRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [startPos, setStartPos] = useState({ x: 0, y: 0 });
  const hasMoved = useRef(false);

  function getSvg(type: string, color: string) {
    if (type === "pawn" && color === "white") return WhitePawn;
    if (type === "knight" && color === "white") return WhiteKnight;
    if (type === "bishop" && color === "white") return WhiteBishop;
    if (type === "rook" && color === "white") return WhiteRook;
    if (type === "queen" && color === "white") return WhiteQueen;
    if (type === "king" && color === "white") return WhiteKing;
    if (type === "pawn" && color === "black") return BlackPawn;
    if (type === "knight" && color === "black") return BlackKnight;
    if (type === "bishop" && color === "black") return BlackBishop;
    if (type === "rook" && color === "black") return BlackRook;
    if (type === "queen" && color === "black") return BlackQueen;
    if (type === "king" && color === "black") return BlackKing;
    // Fallback for unknown piece types
    return WhitePawn;
  }

  useEffect(() => {
    if (!isDragging) return;

    const handlePointerMove = (e: PointerEvent) => {
      const offsetX = e.clientX - startPos.x;
      const offsetY = e.clientY - startPos.y;

      // Consider it a drag if moved more than 5 pixels
      if (Math.abs(offsetX) > 5 || Math.abs(offsetY) > 5) {
        hasMoved.current = true;
      }

      setDragOffset({
        x: offsetX,
        y: offsetY,
      });
    };

    const handlePointerUp = (e: PointerEvent) => {
      setIsDragging(false);
      setDragOffset({ x: 0, y: 0 });

      // Only trigger drop if the piece was actually dragged
      if (hasMoved.current) {
        const boardSquareWidth = boardDimensions.width / 8;
        const boardSquareHeight = boardDimensions.height / 8;
        const offset = boardSquareWidth / 2;

        const x = Math.floor((dragOffset.x + offset) / boardSquareWidth);
        const y = Math.floor((dragOffset.y + offset) / boardSquareHeight);

        onPieceDrop?.(x, y);
      }

      hasMoved.current = false;
    };

    document.addEventListener("pointermove", handlePointerMove);
    document.addEventListener("pointerup", handlePointerUp);

    return () => {
      document.removeEventListener("pointermove", handlePointerMove);
      document.removeEventListener("pointerup", handlePointerUp);
    };
  }, [isDragging, startPos, dragOffset, boardDimensions, onPieceDrop]);

  const handlePointerDown = (e: React.PointerEvent) => {
    if (color !== playerColor || (gameStatus !== "in progress" && gameStatus !== "not started")) {
      return;
    }

    setIsDragging(true);
    setStartPos({ x: e.clientX, y: e.clientY });
    setDragOffset({ x: 0, y: 0 });
    hasMoved.current = false;
  };

  if (!type || !color) {
    return null;
  }

  const svgSrc = getSvg(type, color);
  if (!svgSrc) {
    return null;
  }

  const canDrag = color === playerColor && (gameStatus === "in progress" || gameStatus === "not started");

  const pieceImage = (
    <div
      ref={nodeRef}
      style={{
        position: "relative",
        ...style,
        transform: isDragging ? `translate(${dragOffset.x}px, ${dragOffset.y}px)` : undefined,
        cursor: canDrag ? "grab" : "default",
        touchAction: "none",
        zIndex: isDragging ? 1002 : (color === playerColor ? 1001 : 1000),
      }}
      onPointerDown={handlePointerDown}
    >
      <img
        src={svgSrc}
        alt=""
        style={{
          width: "100%",
          height: "100%",
          pointerEvents: "none",
        }}
        draggable={false}
      />
      {modifiers.length > 0 && (
        <div
          style={{
            position: "absolute",
            top: "2px",
            left: "2px",
            display: "flex",
            gap: "2px",
            padding: "2px",
            backgroundColor: "rgba(0, 0, 0, 0.5)",
            borderRadius: "4px",
            zIndex: 1002,
          }}
        >
          {modifiers.map((modifier, index) => {
            // Handle both string format (from Modifiers page) and object format (from game state)
            const modifierType =
              typeof modifier === "string"
                ? modifier
                : (modifier as any).type || modifier;
            return (
              <div
                key={`${modifierType}-${index}`}
                style={{
                  width: "16px",
                  height: "16px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                {React.cloneElement(
                  modifierIcons[modifierType] || modifierIcons["default"],
                  {
                    style: { width: "14px", height: "14px" },
                  }
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );

  return pieceImage;
});
