import { CSSProperties } from "react";
import { Piece } from "./Piece";
import { Square } from "./Square";

export function Tile({
  type,
  color,
  x,
  y,
  isActive,
  isPossibleMove,
}: {
  type: string;
  color: string;
  x: number;
  y: number;
  isActive: boolean;
  isPossibleMove?: boolean;
}) {
  const pieceStyle: CSSProperties = {
    position: "absolute",
    top: 12.5 * x + "%",
    left: 12.5 * y + "%",
    width: "12.5%",
    height: "12.5%",
  };

  return (
    <>
      <div>
        <Square light={(x + y) % 2 === 0} style={pieceStyle}></Square>
        {isActive && (
          <div
            style={{ ...pieceStyle, backgroundColor: "rgba(20, 85, 30, .5)" }}
          ></div>
        )}
        <Piece type={type} color={color} style={pieceStyle} />
      </div>
      {isPossibleMove && (
        <div
          style={{
            ...pieceStyle,
            background:
              "radial-gradient(rgba(20, 85, 30, 0.5) 19%, rgba(0, 0, 0, 0) 20%)",
          }}
        ></div>
      )}
      {/* <div
        style={{
          ...pieceStyle,
          background:
            "radial-gradient(transparent 0%, transparent 79%, rgba(20, 85, 0, 0.3) 80%)",
        }}
      ></div> */}
    </>
  );
}
