import { useState } from "react";
import { ChessGame } from "../obj/ChessGame";
import { Tile } from "./Tile";
import { socket } from "../socket";

export function Board({
  game,
  updatePossibleMoves,
}: {
  game: ChessGame;
  updatePossibleMoves: (moves: Array<[number, number]>) => void;
}) {
  const [activeSquare, setActiveSquare] = useState<[number, number] | null>(
    null
  );
  const playerColor = game.players?.white === socket.id ? "white" : "black";

  function onSquareClicked(coords: [number, number]) {
    if (game.turn === playerColor) {
      if (isPossibleMove(coords)) {
        if (
          ((playerColor === "white" && coords[0] === 0) ||
            (playerColor === "black" && coords[0] === 7)) &&
          game.board?.squares![activeSquare![0]][activeSquare![1]]?.type ===
            "pawn"
        ) {
          socket.emit("movePiece", {
            from: activeSquare,
            to: coords,
            promotion: "queen",
          });
        } else {
          socket.emit("movePiece", {
            from: activeSquare,
            to: coords,
          });
        }
        setActiveSquare(null);
        updatePossibleMoves([]);
      } else if (game.board?.squares![coords[0]][coords[1]] === null) {
        setActiveSquare(null);
        updatePossibleMoves([]);
      } else if (
        game.board?.squares![coords[0]][coords[1]]?.color === playerColor
      ) {
        setActiveSquare(coords);
        socket.emit("tileClicked", coords);
      } else {
        setActiveSquare(null);
        updatePossibleMoves([]);
      }
    } else {
      setActiveSquare(null);
      updatePossibleMoves([]);
    }
  }

  function isPossibleMove(coords: [number, number]) {
    return (
      game.possibleMoves?.find(
        (move) => move[0] === coords[0] && move[1] === coords[1]
      ) !== undefined
    );
  }

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
      {game.board?.squares &&
        game.board.squares.map((row, i) =>
          row.map((square, j) => (
            <div
              style={{ cursor: "pointer" }}
              onClick={() => onSquareClicked([i, j])}
              key={`tile-div-${i}-${j}`}
            >
              <Tile
                type={square?.type}
                color={square?.color}
                x={playerColor === "white" ? i : 8 - i}
                y={playerColor === "white" ? j : 8 - j}
                isActive={activeSquare?.[0] === i && activeSquare?.[1] === j}
                isPossibleMove={
                  game.possibleMoves?.find(
                    (move) => move[0] === i && move[1] === j
                  ) !== undefined
                }
                isCheck={
                  (square?.type === "king" &&
                    square?.color === "white" &&
                    game.kingsInCheck?.white) ||
                  (square?.type === "king" &&
                    square?.color === "black" &&
                    game.kingsInCheck?.black)
                }
                key={`tile-${i}-${j}`}
              />
            </div>
          ))
        )}
    </div>
  );
}
