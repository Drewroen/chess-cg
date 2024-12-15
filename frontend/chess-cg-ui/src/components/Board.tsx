import { useEffect, useState } from "react";
import { ChessBoard } from "../obj/ChessBoard";
import { Tile } from "./Tile";
import { socket } from "../socket";

export function Board({ board }: { board?: ChessBoard }) {
  const [activeSquare, setActiveSquare] = useState<[number, number] | null>(
    null
  );
  const [possibleMoves, setPossibleMoves] = useState<Array<
    [number, number]
  > | null>(null);

  function onSquareClicked(coords: [number, number]) {
    if (isPossibleMove(coords)) {
      socket.emit("movePiece", {
        from: activeSquare,
        to: coords,
      });
      setActiveSquare(null);
      setPossibleMoves(null);
      return;
    }
    if (board?.squares![coords[0]][coords[1]] === null) {
      setActiveSquare(null);
      setPossibleMoves(null);
      return;
    }
    setActiveSquare(coords);
    socket.emit("tileClicked", coords);
  }

  function isPossibleMove(coords: [number, number]) {
    return (
      possibleMoves?.find(
        (move) => move[0] === coords[0] && move[1] === coords[1]
      ) !== undefined
    );
  }

  useEffect(() => {
    function onTileClick(data: any) {
      const moves: Array<any> = data.map((move: any) => {
        const position = move.position_to_move;
        return [position.row, position.col];
      });
      setPossibleMoves(moves);
    }
    socket.on("tileClicked", onTileClick);

    return () => {
      socket.off("tileClicked");
    };
  }, []);

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
              onClick={() => onSquareClicked([i, j])}
            >
              <Tile
                type={square?.type}
                color={square?.color}
                x={i}
                y={j}
                isActive={activeSquare?.[0] === i && activeSquare?.[1] === j}
                isPossibleMove={
                  possibleMoves?.find(
                    (move) => move[0] === i && move[1] === j
                  ) !== undefined
                }
                key={`${i}-${j}`}
              />
            </div>
          ))
        )}
    </div>
  );
}
