interface GameOverProps {
  isMobile?: boolean;
  winner?: string;
  endReason?: string;
}

function getGameEndMessage(winner?: string, endReason?: string): string {
  if (!winner || !endReason) {
    return "Game Over.";
  }

  const capitalizeColor = (color: string) =>
    color.charAt(0).toUpperCase() + color.slice(1);

  switch (endReason) {
    case "checkmate":
      return `${capitalizeColor(winner)} wins by checkmate.`;
    case "time":
      return `${capitalizeColor(winner)} wins on time.`;
    case "resignation":
      return `${capitalizeColor(winner)} wins by resignation.`;
    case "stalemate":
      return "Stalemate.";
    case "draw_agreement":
      return "Draw.";
    case "aborted":
      return "Game aborted.";
    default:
      if (winner === "draw") {
        return "Game drawn.";
      }
      return winner !== "aborted"
        ? `${capitalizeColor(winner)} wins.`
        : "Game Over.";
  }
}

export function GameOver({
  isMobile = false,
  winner,
  endReason,
}: GameOverProps) {
  const containerStyle = isMobile
    ? {
        display: "flex",
        justifyContent: "center",
        margin: "4px 0",
        width: "100%",
        maxWidth: "600px",
        boxSizing: "border-box" as const,
      }
    : {
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        padding: "4px 0",
      };

  const textStyle = {
    color: "#fff",
    fontSize: isMobile ? "16px" : "18px",
    fontWeight: "500",
    fontFamily: "sans-serif",
  } as const;

  return (
    <div style={containerStyle}>
      <span style={textStyle}>{getGameEndMessage(winner, endReason)}</span>
    </div>
  );
}
