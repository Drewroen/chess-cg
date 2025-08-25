import { useState, useEffect, useRef } from "react";
import { ChessGame, Move, MoveMessage, ResetPremoveMessage } from "../obj/ChessGame";
import { Tile } from "./Tile";
import { PromotionSelector } from "./PromotionSelector";

export function Board({
  game,
  updatePossibleMoves,
  socket,
  onMoveLocal,
  playerColor,
}: {
  game: ChessGame;
  updatePossibleMoves: (moves: Array<[number, number]>) => void;
  socket: WebSocket | null;
  onMoveLocal?: (from: [number, number], to: [number, number]) => void;
  playerColor: string;
}) {
  const [activeSquare, setActiveSquare] = useState<[number, number] | null>(
    null
  );
  const [showPromotion, setShowPromotion] = useState(false);
  const [promotionMove, setPromotionMove] = useState<Move | null>(null);
  const [possibleMoves, setPossibleMoves] = useState<number[][]>([]);
  const [premove, setPremove] = useState<Move | null>(null);
  const [boardDimensions, setBoardDimensions] = useState({
    width: 0,
    height: 0,
  });
  const boardRef = useRef<HTMLDivElement>(null);
  const touchUsedRef = useRef(false);

  // Reset active square when board state changes (e.g., opponent makes a move)
  useEffect(() => {
    setActiveSquare(null);
    setPossibleMoves([]);
  }, [game.board, game.turn]);

  // Clear premove when it's executed or game state changes
  useEffect(() => {
    setPremove(null);
  }, [game.board?.squares]);

  // Track board dimensions with ResizeObserver
  useEffect(() => {
    const resizeObserver = new ResizeObserver((entries) => {
      for (let entry of entries) {
        const { width, height } = entry.contentRect;
        setBoardDimensions({ width, height });
      }
    });

    if (boardRef.current) {
      resizeObserver.observe(boardRef.current);
    }

    return () => resizeObserver.disconnect();
  }, []);

  function onPieceDrop(
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
      const moveMessage: MoveMessage = {
        type: "move",
        from: promotionMove.from,
        to: promotionMove.to,
        promotion: pieceType,
      };
      socket?.send(JSON.stringify(moveMessage));
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
          // Call local move update for instant feedback
          if (onMoveLocal && activeSquare) {
            onMoveLocal(activeSquare, coords);
          }

          if (activeSquare) {
            const moveMessage: MoveMessage = {
              type: "move",
              from: activeSquare,
              to: coords,
            };
            socket?.send(JSON.stringify(moveMessage));
          }
          setActiveSquare(null);
          setPossibleMoves([]);
        }
      } else if (game.board?.squares![coords[0]][coords[1]] === null) {
        setActiveSquare(null);
        setPossibleMoves([]);
      } else if (
        game.board?.squares![coords[0]][coords[1]]?.color === playerColor
      ) {
        let gameMoves = game.moves; // Now simplified to single array
        let availableMoves = [];
        for (let move of gameMoves) {
          let from = move.from;
          if (from.row === coords[0] && from.col === coords[1]) {
            availableMoves.push([move.to.row, move.to.col]);
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
          if (activeSquare) {
            const moveMessage: MoveMessage = {
              type: "move",
              from: activeSquare,
              to: coords,
            };
            socket?.send(JSON.stringify(moveMessage));
          }
          // Set the premove for visualization
          setPremove({ from: activeSquare!, to: coords });
          setActiveSquare(null);
          setPossibleMoves([]);
        }
      } else if (
        game.board?.squares![coords[0]][coords[1]]?.color === playerColor &&
        !activeSquare
      ) {
        let gamePremoves = game.moves; // Now simplified to single array (premoves when not your turn)
        let availablePremoves = [];
        for (let premove of gamePremoves) {
          let from = premove.from;
          if (from.row === coords[0] && from.col === coords[1]) {
            availablePremoves.push([premove.to.row, premove.to.col]);
          }
        }
        setPossibleMoves(availablePremoves);
        setActiveSquare(coords);
      } else {
        // Clicked on empty square or opponent piece - reset premove
        const resetMessage: ResetPremoveMessage = {
          type: "reset_premove",
        };
        socket?.send(JSON.stringify(resetMessage));
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
      ref={boardRef}
      style={{
        position: "relative",
        width: "100%",
        aspectRatio: "1 / 1",
        maxWidth: "600px",
        maxHeight: "600px",
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
                if (touchUsedRef.current) {
                  touchUsedRef.current = false;
                  return;
                }
                onSquareClicked([i, j]);
              }}
              onTouchStart={() => {
                touchUsedRef.current = true;
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
                onPieceDrop={(dragX, dragY) => onPieceDrop(dragX, dragY, i, j)}
                isPremove={
                  !!premove &&
                  ((premove.from[0] === i && premove.from[1] === j) ||
                    (premove.to[0] === i && premove.to[1] === j))
                }
                boardDimensions={boardDimensions}
                gameStatus={game.status}
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
