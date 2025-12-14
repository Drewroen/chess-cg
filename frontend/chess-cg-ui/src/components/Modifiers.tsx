import { useState, useEffect } from "react";
import styles from "./Modifiers.module.css";
import { Square } from "./Square";
import { Piece } from "./Piece";
import { modifierIcons } from "../utils/modifierIcons";
import { backendUrl } from "../config/environment";

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
  // Track selected modifiers for each piece: key is "color-row-col", value is array of modifier types
  const [selectedModifiers, setSelectedModifiers] = useState<
    Record<string, string[]>
  >({});
  const squareSize = isMobile ? 40 : 60;
  const boardDimensions = { width: squareSize * 8, height: squareSize * 2 };

  // Reset selection when color changes
  const handleColorChange = (newColor: "white" | "black") => {
    setPieceColor(newColor);
    setSelectedPiece(null);
  };

  // Toggle modifier selection for current piece
  const toggleModifier = (modifierType: string) => {
    if (!selectedPiece) return;

    const pieceKey = `${pieceColor}-${selectedPiece.row}-${selectedPiece.col}`;
    const currentSelections = selectedModifiers[pieceKey] || [];

    if (currentSelections.includes(modifierType)) {
      // Remove modifier
      setSelectedModifiers({
        ...selectedModifiers,
        [pieceKey]: currentSelections.filter((m) => m !== modifierType),
      });
    } else {
      // Add modifier
      setSelectedModifiers({
        ...selectedModifiers,
        [pieceKey]: [...currentSelections, modifierType],
      });
    }
  };

  // Check if modifier is selected for current piece
  const isModifierSelected = (modifierType: string): boolean => {
    if (!selectedPiece) return false;
    const pieceKey = `${pieceColor}-${selectedPiece.row}-${selectedPiece.col}`;
    return selectedModifiers[pieceKey]?.includes(modifierType) || false;
  };

  // Save loadout - convert selectedModifiers to backend format
  const handleSaveLoadout = async () => {
    const loadout = Object.entries(selectedModifiers).map(([pieceKey, modifiers]) => {
      const [color, rowStr, colStr] = pieceKey.split('-');
      const uiRow = parseInt(rowStr);
      const col = parseInt(colStr);

      // Determine piece type based on row and col
      let pieceType: string;
      if (uiRow === 0) {
        pieceType = 'pawn';
      } else {
        const piece = initialWhitePieces.find(p => p.col === col);
        pieceType = piece?.type || 'pawn';
      }

      // Map UI rows to backend board positions
      // UI: row 0 = pawns, row 1 = pieces
      // Backend white: row 6 = pawns, row 7 = pieces
      // Backend black: row 1 = pawns, row 0 = pieces
      let backendRow: number;
      if (color === 'white') {
        backendRow = uiRow === 0 ? 6 : 7;
      } else {
        backendRow = uiRow === 0 ? 1 : 0;
      }

      return {
        color,
        piece_type: pieceType,
        position: { row: backendRow, col },
        modifiers
      };
    });

    const payload = { loadout };
    console.log('Sending loadout to backend:');
    console.log(JSON.stringify(payload, null, 2));

    try {
      const response = await fetch(
        `${backendUrl}/api/game/loadout/save`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include', // Include cookies for authentication
          body: JSON.stringify(payload),
        }
      );

      const data = await response.json();

      if (response.ok) {
        console.log('Loadout saved successfully:');
        console.log(data);
        alert('Loadout saved successfully!');
      } else {
        console.error('Loadout save failed:');
        console.error(data);
        alert(`Save failed:\n${data.detail?.errors?.join('\n') || data.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Failed to save loadout:', error);
      alert('Failed to connect to server');
    }
  };

  useEffect(() => {
    const fetchModifiers = async () => {
      try {
        const response = await fetch(
          `${backendUrl}/api/game/modifiers`
        );
        const data = await response.json();
        setModifiers(data.modifiers);
      } catch (error) {
        console.error("Failed to fetch modifiers:", error);
      }
    };

    const fetchLoadout = async () => {
      try {
        const response = await fetch(
          `${backendUrl}/api/game/loadout`,
          {
            credentials: "include", // Include cookies for authentication
          }
        );

        if (response.ok) {
          const data = await response.json();

          if (data.loadout && data.loadout.loadout) {
            // Convert backend loadout format to frontend selectedModifiers format
            const modifiersMap: Record<string, string[]> = {};

            data.loadout.loadout.forEach((piece: any) => {
              const { color, position, modifiers } = piece;

              // Map backend positions to UI rows
              // Backend white: row 6 = pawns, row 7 = pieces
              // Backend black: row 1 = pawns, row 0 = pieces
              // UI: row 0 = pawns, row 1 = pieces
              let uiRow: number;
              if (color === 'white') {
                uiRow = position.row === 6 ? 0 : 1;
              } else {
                uiRow = position.row === 1 ? 0 : 1;
              }

              const pieceKey = `${color}-${uiRow}-${position.col}`;
              modifiersMap[pieceKey] = modifiers;
            });

            setSelectedModifiers(modifiersMap);
            console.log('Loaded existing loadout:', modifiersMap);
          }
        } else if (response.status === 401) {
          console.log('User not authenticated, skipping loadout fetch');
        } else {
          console.error('Failed to fetch loadout:', response.status);
        }
      } catch (error) {
        console.error("Failed to fetch loadout:", error);
      }
    };

    fetchModifiers();
    fetchLoadout();
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
      <button className={styles.saveButton} onClick={handleSaveLoadout}>
        Save Loadout
      </button>
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
                        modifiers={
                          selectedModifiers[
                            `${pieceColor}-${row}-${col}`
                          ] || []
                        }
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
              <div className={styles.modifierCards}>
                {availableModifiers.map((modifier) => {
                  const isSelected = isModifierSelected(modifier.type);
                  return (
                    <div
                      key={modifier.type}
                      className={`${styles.modifierCard} ${
                        isSelected ? styles.selected : ""
                      }`}
                      onClick={() => toggleModifier(modifier.type)}
                    >
                      <div className={styles.iconContainer}>
                        {modifierIcons[modifier.type] || modifierIcons["default"]}
                      </div>
                      <div className={styles.modifierContent}>
                        <div className={styles.modifierHeader}>
                          <h4>{modifier.type}</h4>
                          <span className={styles.modifierScore}>
                            +{modifier.score}
                            {modifier.score === 25 ? "%" : ""}
                          </span>
                        </div>
                        <p className={styles.modifierDescription}>
                          {modifier.description}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p>No modifiers available for this piece.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
