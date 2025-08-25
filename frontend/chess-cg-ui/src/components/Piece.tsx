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
import { CSSProperties, useRef } from "react";
import Draggable from "react-draggable";

export function Piece({
  type,
  color,
  style,
  playerColor,
  onPieceDrop,
  boardDimensions,
  gameStatus,
}: {
  type?: string;
  color?: string;
  style: CSSProperties;
  playerColor: string;
  onPieceDrop?: (x: number, y: number) => void;
  boardDimensions: { width: number; height: number };
  gameStatus?: string;
}) {
  const nodeRef = useRef(null);
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
  }

  if (!type || !color) {
    return null;
  }

  const svgSrc = getSvg(type, color);
  if (!svgSrc) {
    return null;
  }

  const pieceImage = (
    <img
      ref={nodeRef}
      src={svgSrc}
      alt=""
      style={{ ...style, zIndex: color === playerColor ? 1001 : 1000 }}
      draggable={false}
    />
  );

  return color === playerColor &&
    (gameStatus === "in progress" || gameStatus === "not started") ? (
    <Draggable
      nodeRef={nodeRef}
      position={{ x: 0, y: 0 }}
      onStop={(_e, data) => {
        const boardSquareWidth = boardDimensions.width / 8;
        const boardSquareHeight = boardDimensions.height / 8;
        const offset = boardSquareWidth / 2;

        const x = Math.floor((data.x + offset) / boardSquareWidth);
        const y = Math.floor((data.y + offset) / boardSquareHeight);

        onPieceDrop?.(x, y);
      }}
    >
      {pieceImage}
    </Draggable>
  ) : (
    pieceImage
  );
}
