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
import Empty from "../assets/empty.svg";
import { CSSProperties } from "react";

export function Piece({
  type,
  color,
  style,
}: {
  type: string;
  color: string;
  style: CSSProperties;
}) {
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
    return Empty;
  }

  return <img src={getSvg(type, color)} alt="" style={style} />;
}
