import { ChessBoard } from "../obj/ChessBoard";
import { Piece } from "./Piece";

export function Board({ board }: { board: ChessBoard | null }) {
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
        width: "600px",
        height: "600px",
        padding: 0,
        margin: 0,
      }}
    >
      {board?.squares &&
        board.squares.map((row, i) =>
          row.map((square, j) => (
            <Piece type={square?.type} color={square?.color} x={i} y={j} />
          ))
        )}
    </div>
  );
}
