import { useState, useEffect } from "react";
import styles from "./Modifiers.module.css";
import { Square } from "./Square";
import { Piece } from "./Piece";
import { Button } from "./Button";
import { modifierIcons } from "../utils/modifierIcons";
import { backendUrl } from "../config/environment";

interface ModifiersProps {
  isMobile?: boolean;
  onBack?: () => void;
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

export const Modifiers = ({ isMobile, onBack }: ModifiersProps) => {
  const [modifiers, setModifiers] = useState<Modifier[]>([]);
  const [selectedPiece, setSelectedPiece] = useState<{
    type: string;
    row: number;
    col: number;
    color: "white" | "black";
  } | null>(null);
  // Track selected modifiers for each piece: key is "color-row-col", value is array of modifier types
  const [selectedModifiers, setSelectedModifiers] = useState<
    Record<string, string[]>
  >({});
  const squareSize = isMobile ? 40 : 60;
  const boardDimensions = { width: squareSize * 8, height: squareSize * 2 };

  // Toggle modifier selection for current piece (single modifier per piece)
  const toggleModifier = (modifierType: string) => {
    if (!selectedPiece) return;

    const pieceKey = `${selectedPiece.color}-${selectedPiece.row}-${selectedPiece.col}`;
    const currentSelections = selectedModifiers[pieceKey] || [];

    if (currentSelections.includes(modifierType)) {
      // Remove modifier
      setSelectedModifiers({
        ...selectedModifiers,
        [pieceKey]: [],
      });
    } else {
      // Replace with new modifier (enforces single-modifier constraint)
      setSelectedModifiers({
        ...selectedModifiers,
        [pieceKey]: [modifierType],
      });
    }
  };

  // Check if modifier is selected for current piece
  const isModifierSelected = (modifierType: string): boolean => {
    if (!selectedPiece) return false;
    const pieceKey = `${selectedPiece.color}-${selectedPiece.row}-${selectedPiece.col}`;
    return selectedModifiers[pieceKey]?.includes(modifierType) || false;
  };

  const handleSaveLoadout = async () => {
    const white: Array<{ pos: [number, number]; modifier: string }> = [];
    const black: Array<{ pos: [number, number]; modifier: string }> = [];

    Object.entries(selectedModifiers).forEach(([pieceKey, modifiers]) => {
      const [color, rowStr, colStr] = pieceKey.split("-");
      const uiRow = parseInt(rowStr);
      const col = parseInt(colStr);

      // Map UI rows to backend board positions
      // UI: row 0 = pawns, row 1 = pieces
      // Backend white: row 6 = pawns, row 7 = pieces
      // Backend black: row 1 = pawns, row 0 = pieces
      let backendRow: number;
      if (color === "white") {
        backendRow = uiRow === 0 ? 6 : 7;
      } else {
        backendRow = uiRow === 0 ? 1 : 0;
      }

      // Only take FIRST modifier (single modifier constraint)
      const firstModifier = modifiers[0];
      if (firstModifier) {
        const pieceData = { pos: [backendRow, col] as [number, number], modifier: firstModifier };
        if (color === "white") {
          white.push(pieceData);
        } else {
          black.push(pieceData);
        }
      }
    });

    const payload = { white, black };
    console.log("Sending loadout to backend:");
    console.log(JSON.stringify(payload, null, 2));

    try {
      const response = await fetch(`${backendUrl}/api/game/loadout/save`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include", // Include cookies for authentication
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (response.ok) {
        console.log("Loadout saved successfully:");
        console.log(data);
        alert("Loadout saved successfully!");
        onBack?.();
      } else {
        console.error("Loadout save failed:");
        console.error(data);
        alert(
          `Save failed:\n${
            data.detail?.errors?.join("\n") || data.detail || "Unknown error"
          }`
        );
      }
    } catch (error) {
      console.error("Failed to save loadout:", error);
      alert("Failed to connect to server");
    }
  };

  useEffect(() => {
    const fetchModifiers = async () => {
      try {
        const response = await fetch(`${backendUrl}/api/game/modifiers`);
        const data = await response.json();
        setModifiers(data.modifiers);
      } catch (error) {
        console.error("Failed to fetch modifiers:", error);
      }
    };

    const fetchLoadout = async () => {
      try {
        const response = await fetch(`${backendUrl}/api/game/loadout`, {
          credentials: "include", // Include cookies for authentication
        });

        if (response.ok) {
          const data = await response.json();

          if (data.loadout) {
            // Convert backend loadout format to frontend selectedModifiers format
            const loadoutData = data.loadout;
            const white = loadoutData.white || [];
            const black = loadoutData.black || [];

            const modifiersMap: Record<string, string[]> = {};

            // Process white pieces
            white.forEach((piece: any) => {
              const [row, col] = piece.pos;

              // Map backend positions to UI rows
              // Backend white: row 6 = pawns, row 7 = pieces
              // UI: row 0 = pawns, row 1 = pieces
              const uiRow = row === 6 ? 0 : 1;

              const pieceKey = `white-${uiRow}-${col}`;
              // Store as array with single item for compatibility
              modifiersMap[pieceKey] = piece.modifier ? [piece.modifier] : [];
            });

            // Process black pieces
            black.forEach((piece: any) => {
              const [row, col] = piece.pos;

              // Map backend positions to UI rows
              // Backend black: row 1 = pawns, row 0 = pieces
              // UI: row 0 = pawns, row 1 = pieces
              const uiRow = row === 1 ? 0 : 1;

              const pieceKey = `black-${uiRow}-${col}`;
              // Store as array with single item for compatibility
              modifiersMap[pieceKey] = piece.modifier ? [piece.modifier] : [];
            });

            setSelectedModifiers(modifiersMap);
            console.log("Loaded existing loadout:", modifiersMap);
          }
        } else if (response.status === 401) {
          console.log("User not authenticated, skipping loadout fetch");
        } else {
          console.error("Failed to fetch loadout:", response.status);
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

  const renderBoardSection = (color: "white" | "black") => {
    return (
      <div className={styles.colorSection}>
        <h3 className={styles.colorTitle}>
          {color.charAt(0).toUpperCase() + color.slice(1)} Loadout
        </h3>
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
                  selectedPiece?.col === col &&
                  selectedPiece?.color === color;

                return (
                  <div
                    key={`${row}-${col}`}
                    className={styles.squareWrapper}
                    onClick={() => {
                      if (!piece) return;
                      // Toggle selection: deselect if clicking the same piece
                      if (
                        selectedPiece?.row === row &&
                        selectedPiece?.col === col &&
                        selectedPiece?.color === color
                      ) {
                        setSelectedPiece(null);
                      } else {
                        setSelectedPiece({ type: piece.type, row, col, color });
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
                        color={color}
                        style={{
                          width: squareSize,
                          height: squareSize,
                          position: "absolute",
                          top: 0,
                          left: 0,
                        }}
                        playerColor={color}
                        boardDimensions={boardDimensions}
                        gameStatus="completed"
                        modifiers={
                          selectedModifiers[`${color}-${row}-${col}`] || []
                        }
                      />
                    )}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div
      className={`${styles.modifiersContainer} ${
        isMobile ? styles.mobile : ""
      }`}
    >
      <h2>Modifiers</h2>
      <p className={styles.subtitle}>
        Select a piece to view and apply available modifiers that enhance its
        abilities. Customize your loadout for both white and black pieces.
      </p>
      <div className={styles.contentWrapper}>
        {renderBoardSection("white")}
        {renderBoardSection("black")}
        <div className={styles.buttonContainer}>
          {onBack && (
            <Button onClick={onBack} variant="neutral" isMobile={isMobile}>
              Back
            </Button>
          )}
          <Button
            onClick={handleSaveLoadout}
            variant="primary"
            isMobile={isMobile}
          >
            Save
          </Button>
        </div>
        {selectedPiece && (
          <div className={styles.modifierList}>
            <h3>
              {selectedPiece.color.charAt(0).toUpperCase() +
                selectedPiece.color.slice(1)}{" "}
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
                        {modifierIcons[modifier.type] ||
                          modifierIcons["default"]}
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
