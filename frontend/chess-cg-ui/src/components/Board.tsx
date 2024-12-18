import { useEffect, useState } from "react";
import { ChessBoard, ChessGame } from "../obj/ChessGame";
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

  console.log(game.possibleMoves);
  console.log("WHAT");

  function onSquareClicked(coords: [number, number]) {
    if (isPossibleMove(coords)) {
      socket.emit("movePiece", {
        from: activeSquare,
        to: coords,
      });
      setActiveSquare(null);
      updatePossibleMoves([]);
      return;
    }
    if (game.board?.squares![coords[0]][coords[1]] === null) {
      setActiveSquare(null);
      updatePossibleMoves([]);
      return;
    }
    setActiveSquare(coords);
    socket.emit("tileClicked", coords);
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
                x={i}
                y={j}
                isActive={activeSquare?.[0] === i && activeSquare?.[1] === j}
                isPossibleMove={
                  game.possibleMoves?.find(
                    (move) => move[0] === i && move[1] === j
                  ) !== undefined
                }
                key={`tile-${i}-${j}`}
              />
            </div>
          ))
        )}
    </div>
  );
}
