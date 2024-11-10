import { ChessBoard } from "../obj/ChessBoard";

export function Board({ board }: { board: ChessBoard | null }) {
  console.log(board);
  return (
    <div>
      {board?.squares && (
        <table>
          <tbody>
            {board.squares.map((row, i) => (
              <tr key={i}>
                {row.map((square, j) => (
                  <td key={j}>
                    {square ? MapPieceToSymbol(square.type, square.color) : "□"}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

function MapPieceToSymbol(piece: string = "", color: string = "") {
  const symbols: { [key: string]: { white: string; black: string } } = {
    pawn: { white: "♙", black: "♟" },
    knight: { white: "♘", black: "♞" },
    bishop: { white: "♗", black: "♝" },
    rook: { white: "♖", black: "♜" },
    queen: { white: "♕", black: "♛" },
    king: { white: "♔", black: "♚" },
  };

  if (piece in symbols) {
    if (color === "white" || color === "black") {
      return symbols[piece][color];
    }
  }
  return "";
}
