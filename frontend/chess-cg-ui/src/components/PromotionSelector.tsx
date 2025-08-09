import { CSSProperties } from "react";
import { Piece } from "./Piece";

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
            <Piece
              type={type}
              color={playerColor}
              style={{ width: "100%", height: "100%" }}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
