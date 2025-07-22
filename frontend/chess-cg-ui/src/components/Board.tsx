import { useState } from "react";
import { ChessGame } from "../obj/ChessGame";
import { Tile } from "./Tile";
import { PromotionSelector } from "./PromotionSelector";

export function Board({
  game,
  updatePossibleMoves,
  socket,
}: {
  game: ChessGame;
  updatePossibleMoves: (moves: Array<[number, number]>) => void;
  socket: WebSocket | null;
}) {
  const [activeSquare, setActiveSquare] = useState<[number, number] | null>(
    null
  );
  const [showPromotion, setShowPromotion] = useState(false);
  const [promotionMove, setPromotionMove] = useState<{
    from: [number, number];
    to: [number, number];
  } | null>(null);
  const playerColor = game.players?.white.id === game.id ? "white" : "black";
  const [possibleMoves, setPossibleMoves] = useState<number[][]>([]);

  function handlePromotion(pieceType: string) {
    if (promotionMove) {
      socket?.send(
        JSON.stringify({
          from: promotionMove.from,
          to: promotionMove.to,
          promotion: pieceType,
        })
      );
      setPromotionMove(null);
      setShowPromotion(false);
      setActiveSquare(null);
      setPossibleMoves([]);
    }
  }

  function onSquareClicked(coords: [number, number]) {
    if (game.turn === playerColor && game.status !== "complete") {
      if (isPossibleMove(coords)) {
        if (
          ((playerColor === "white" && coords[0] === 0) ||
            (playerColor === "black" && coords[0] === 7)) &&
          game.board?.squares![activeSquare![0]][activeSquare![1]]?.type ===
            "pawn"
        ) {
          // Show promotion selector instead of auto-promoting
          setPromotionMove({ from: activeSquare!, to: coords });
          setShowPromotion(true);
        } else {
          socket?.send(
            JSON.stringify({
              from: activeSquare,
              to: coords,
            })
          );
          setActiveSquare(null);
          setPossibleMoves([]);
        }
      } else if (game.board?.squares![coords[0]][coords[1]] === null) {
        setActiveSquare(null);
        setPossibleMoves([]);
      } else if (
        game.board?.squares![coords[0]][coords[1]]?.color === playerColor
      ) {
        let gameMoves = game.moves[playerColor];
        let availableMoves = [];
        for (let move of gameMoves) {
          let from = move[0];
          if (from[0] === coords[0] && from[1] === coords[1]) {
            availableMoves.push(move[1]);
          }
        }
        setPossibleMoves(availableMoves);
        setActiveSquare(coords);
      } else {
        setActiveSquare(null);
        setPossibleMoves([]);
      }
    } else {
      setActiveSquare(null);
      setPossibleMoves([]);
    }
  }

  function isPossibleMove(coords: [number, number]) {
    return (
      possibleMoves?.find(
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
                x={playerColor === "white" ? i : 7 - i}
                y={playerColor === "white" ? j : 7 - j}
                isActive={activeSquare?.[0] === i && activeSquare?.[1] === j}
                isPossibleMove={possibleMoves.some(
                  (move) => move[0] === i && move[1] === j
                )}
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
      {/* Promotion Selector */}
      <PromotionSelector
        isVisible={showPromotion}
        playerColor={playerColor}
        onSelect={handlePromotion}
      />
    </div>
  );
}
