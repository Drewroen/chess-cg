import { useState } from "react";
import { ChessBoard } from "../obj/ChessBoard";
import { Tile } from "./Tile";

export function Board({ board }: { board?: ChessBoard }) {
  const [activeSquare, setActiveSquare] = useState<[number, number] | null>(
    null
  );

  return (
    <div
      style={{
        position: "relative",
        width: "600px",
        height: "600px",
        padding: 0,
        margin: 0,
      }}
    >
      {board?.squares &&
        board.squares.map((row, i) =>
          row.map((square, j) => (
            <div
              style={{ cursor: "pointer" }}
              onClick={() => setActiveSquare([i, j])}
            >
              <Tile
                type={square?.type}
                color={square?.color}
                x={i}
                y={j}
                isActive={activeSquare?.[0] === i && activeSquare?.[1] === j}
              />
            </div>
          ))
        )}
    </div>
  );
}
