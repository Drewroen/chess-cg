import { CSSProperties } from "react";
import BlackQueen from "../assets/black_queen.svg";
import BlackRook from "../assets/black_rook.svg";
import BlackBishop from "../assets/black_bishop.svg";
import BlackKnight from "../assets/black_knight.svg";
import WhiteQueen from "../assets/white_queen.svg";
import WhiteRook from "../assets/white_rook.svg";
import WhiteBishop from "../assets/white_bishop.svg";
import WhiteKnight from "../assets/white_knight.svg";

interface PromotionSelectorProps {
  isVisible: boolean;
  playerColor: string;
  onSelect: (pieceType: string) => void;
}

export function PromotionSelector({
  isVisible,
  playerColor,
  onSelect,
}: PromotionSelectorProps) {
  if (!isVisible) return null;

  const pieceTypes = ["queen", "rook", "bishop", "knight"];

  function getPieceSvg(type: string, color: string) {
    if (type === "queen" && color === "white") return WhiteQueen;
    if (type === "rook" && color === "white") return WhiteRook;
    if (type === "bishop" && color === "white") return WhiteBishop;
    if (type === "knight" && color === "white") return WhiteKnight;
    if (type === "queen" && color === "black") return BlackQueen;
    if (type === "rook" && color === "black") return BlackRook;
    if (type === "bishop" && color === "black") return BlackBishop;
    if (type === "knight" && color === "black") return BlackKnight;
    return WhiteQueen; // fallback
  }

  const containerStyle: CSSProperties = {
    position: "absolute",
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    backgroundColor: "rgba(255, 255, 255, 0.9)",
    boxShadow: "0 0 15px rgba(0, 0, 0, 0.5)",
    padding: "10px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "10px",
    zIndex: 1000,
  };

  const piecesContainerStyle: CSSProperties = {
    display: "flex",
    gap: "10px",
  };

  const pieceStyle: CSSProperties = {
    width: "60px",
    height: "60px",
    cursor: "pointer",
    padding: "5px",
    transition: "background-color",
  };

  const hoverStyle: CSSProperties = {
    backgroundColor: "rgba(200, 200, 200, 0.5)",
  };

  return (
    <div style={containerStyle}>
      <div style={piecesContainerStyle}>
        {pieceTypes.map((type) => (
          <div
            key={type}
            style={pieceStyle}
            onClick={() => onSelect(type)}
            onMouseOver={(e) => {
              Object.assign(e.currentTarget.style, hoverStyle);
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.backgroundColor = "";
            }}
          >
            <img
              src={getPieceSvg(type, playerColor)}
              alt={`${playerColor} ${type}`}
              style={{ width: "100%", height: "100%" }}
              draggable={false}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
