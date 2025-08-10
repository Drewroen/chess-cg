import { useState, useEffect } from "react";
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
  const [premove, setPremove] = useState<{
    from: [number, number];
    to: [number, number];
  } | null>(null);

  // Reset active square when board state changes (e.g., opponent makes a move)
  useEffect(() => {
    setActiveSquare(null);
    setPossibleMoves([]);
  }, [game.board, game.turn]);

  // Clear premove when it's executed or game state changes
  useEffect(() => {
    setPremove(null);
  }, [game.board?.squares]);

  function handlePieceDrop(
    dragX: number,
    dragY: number,
    boardX: number,
    boardY: number
  ) {
    const newX = playerColor === "white" ? boardX + dragY : boardX - dragY;
    const newY = playerColor === "white" ? boardY + dragX : boardY - dragX;
    if (newX !== boardX || newY !== boardY) onSquareClicked([newX, newY]);
  }

  function handlePromotion(pieceType: string) {
    if (promotionMove) {
      if (game.turn !== playerColor) {
        setPremove({ from: promotionMove.from, to: promotionMove.to });
      }
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
    if (game.status === "complete") {
      setActiveSquare(null);
      setPossibleMoves([]);
      return;
    }

    if (game.turn === playerColor) {
      // It's the player's turn - show regular moves
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
      // It's not the player's turn - handle premoves
      if (isPossibleMove(coords)) {
        if (
          ((playerColor === "white" && coords[0] === 0) ||
            (playerColor === "black" && coords[0] === 7)) &&
          game.board?.squares![activeSquare![0]][activeSquare![1]]?.type ===
            "pawn"
        ) {
          // Show promotion selector for premove
          setPromotionMove({ from: activeSquare!, to: coords });
          setShowPromotion(true);
        } else {
          // Send the premove to the backend
          socket?.send(
            JSON.stringify({
              from: activeSquare,
              to: coords,
            })
          );
          // Set the premove for visualization
          setPremove({ from: activeSquare!, to: coords });
          setActiveSquare(null);
          setPossibleMoves([]);
        }
      } else if (
        game.board?.squares![coords[0]][coords[1]]?.color === playerColor &&
        !activeSquare
      ) {
        let gamePremoves = game.premoves[playerColor];
        let availablePremoves = [];
        for (let premove of gamePremoves) {
          let from = premove[0];
          if (from[0] === coords[0] && from[1] === coords[1]) {
            availablePremoves.push(premove[1]);
          }
        }
        setPossibleMoves(availablePremoves);
        setActiveSquare(coords);
      } else {
        // Clicked on empty square or opponent piece - reset premove
        socket?.send(
          JSON.stringify({
            from: null,
            to: null,
          })
        );
        // Reset premove state
        setPremove(null);
        setActiveSquare(null);
        setPossibleMoves([]);
      }
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
              onMouseDown={() => {
                onSquareClicked([i, j]);
              }}
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
                isPlayerTurn={game.turn === playerColor}
                isCheck={
                  (square?.type === "king" &&
                    square?.color === "white" &&
                    game.kingsInCheck?.white) ||
                  (square?.type === "king" &&
                    square?.color === "black" &&
                    game.kingsInCheck?.black)
                }
                playerColor={playerColor}
                onPieceDrop={(dragX, dragY) =>
                  handlePieceDrop(dragX, dragY, i, j)
                }
                isPremove={
                  !!premove &&
                  ((premove.from[0] === i && premove.from[1] === j) ||
                    (premove.to[0] === i && premove.to[1] === j))
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
