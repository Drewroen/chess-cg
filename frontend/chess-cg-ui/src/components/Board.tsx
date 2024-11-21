import { useState } from "react";
import { ChessBoard } from "../obj/ChessBoard";
import { Piece } from "./Piece";

export function Board({ board }: { board: ChessBoard | null }) {
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
              <Piece
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
