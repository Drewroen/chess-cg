import { ChessBoard } from "../obj/ChessBoard";
import { Piece } from "./Piece";

export function Board({
  board,
  size,
}: {
  board: ChessBoard | null;
  size: number;
}) {
  return (
    // <div style={{ position: "relative", width: 500, height: 500 }}>
    //   {board?.squares && (
    //       {board.squares.map((row, i) => (
    //           {row.map((square, j) => (
    //             <Piece type={square?.type} color={square?.color} x={i} y={j} />
    //           ))}
    //       ))}}
    //   )}
    // </div>
    <div
      style={{
        position: "relative",
        width: size,
        height: size,
        padding: 0,
        margin: 0,
      }}
    >
      {board?.squares &&
        board.squares.map((row, i) =>
          row.map((square, j) => (
            <Piece
              type={square?.type}
              color={square?.color}
              x={i}
              y={j}
              size={size / 8}
            />
          ))
        )}
    </div>
  );
}
