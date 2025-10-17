import { useState, useEffect } from "react";
import styles from "./Modifiers.module.css";
import { Square } from "./Square";
import { Piece } from "./Piece";

interface ModifiersProps {
  isMobile?: boolean;
}

interface Modifier {
  type: string;
  score: number;
  applicable_piece: string;
  description: string;
  uses: number;
}

// Initial white piece setup
const initialWhitePieces = [
  { type: "rook", col: 0 },
  { type: "knight", col: 1 },
  { type: "bishop", col: 2 },
  { type: "queen", col: 3 },
  { type: "king", col: 4 },
  { type: "bishop", col: 5 },
  { type: "knight", col: 6 },
  { type: "rook", col: 7 },
];

export const Modifiers = ({ isMobile }: ModifiersProps) => {
  const [pieceColor, setPieceColor] = useState<"white" | "black">("white");
  const [modifiers, setModifiers] = useState<Modifier[]>([]);
  const [selectedPiece, setSelectedPiece] = useState<{
    type: string;
    row: number;
    col: number;
  } | null>(null);
  const squareSize = isMobile ? 40 : 60;
  const boardDimensions = { width: squareSize * 8, height: squareSize * 2 };

  // Reset selection when color changes
  const handleColorChange = (newColor: "white" | "black") => {
    setPieceColor(newColor);
    setSelectedPiece(null);
  };

  useEffect(() => {
    const fetchModifiers = async () => {
      try {
        const response = await fetch(
          "http://localhost:8000/api/game/modifiers"
        );
        const data = await response.json();
        setModifiers(data.modifiers);
      } catch (error) {
        console.error("Failed to fetch modifiers:", error);
      }
    };

    fetchModifiers();
  }, []);

  const availableModifiers = selectedPiece
    ? modifiers.filter((m) => m.applicable_piece === selectedPiece.type)
    : [];

  return (
    <div
      className={`${styles.modifiersContainer} ${
        isMobile ? styles.mobile : ""
      }`}
    >
      <h2>Modifiers</h2>
      <div className={styles.toggleContainer}>
        <span className={styles.toggleLabel}>White</span>
        <label className={styles.switch}>
          <input
            type="checkbox"
            checked={pieceColor === "black"}
            onChange={(e) =>
              handleColorChange(e.target.checked ? "black" : "white")
            }
          />
          <span className={styles.slider}></span>
        </label>
        <span className={styles.toggleLabel}>Black</span>
      </div>
      <div className={styles.contentWrapper}>
        <div className={styles.boardPreview}>
          {/* Render 2 rows (row 0 = pawns, row 1 = pieces) */}
          {[0, 1].map((row) => (
            <div key={row} className={styles.boardRow}>
              {[0, 1, 2, 3, 4, 5, 6, 7].map((col) => {
                const isLight = (row + col) % 2 === 0;
                const piece =
                  row === 1
                    ? initialWhitePieces.find((p) => p.col === col)
                    : { type: "pawn", col };

                const isSelected =
                  piece &&
                  selectedPiece?.row === row &&
                  selectedPiece?.col === col;

                return (
                  <div
                    key={`${row}-${col}`}
                    className={styles.squareWrapper}
                    onClick={() => {
                      if (!piece) return;
                      // Toggle selection: deselect if clicking the same piece
                      if (
                        selectedPiece?.row === row &&
                        selectedPiece?.col === col
                      ) {
                        setSelectedPiece(null);
                      } else {
                        setSelectedPiece({ type: piece.type, row, col });
                      }
                    }}
                    style={{ cursor: "pointer" }}
                  >
                    <Square
                      light={isLight}
                      style={{
                        width: squareSize,
                        height: squareSize,
                        position: "relative",
                      }}
                    />
                    {isSelected && (
                      <div
                        className={styles.selectedHighlight}
                        style={{
                          width: squareSize,
                          height: squareSize,
                        }}
                      />
                    )}
                    {piece && (
                      <Piece
                        type={piece.type}
                        color={pieceColor}
                        style={{
                          width: squareSize,
                          height: squareSize,
                          position: "absolute",
                          top: 0,
                          left: 0,
                        }}
                        playerColor={pieceColor}
                        boardDimensions={boardDimensions}
                        gameStatus="completed"
                      />
                    )}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
        {selectedPiece && (
          <div className={styles.modifierList}>
            <h3>
              {selectedPiece.type.charAt(0).toUpperCase() +
                selectedPiece.type.slice(1)}
            </h3>
            {availableModifiers.length > 0 ? (
              <ul>
                {availableModifiers.map((modifier) => (
                  <li key={modifier.type}>
                    <strong>{modifier.type}</strong> +{modifier.score}
                    <p>{modifier.description}</p>
                    {modifier.uses > 0 && <em>Uses: {modifier.uses}</em>}
                  </li>
                ))}
              </ul>
            ) : (
              <p>No modifiers available for this piece.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
