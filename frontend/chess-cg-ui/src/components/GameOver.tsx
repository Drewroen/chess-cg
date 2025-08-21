interface GameOverProps {
  isMobile?: boolean;
}

export function GameOver({ isMobile = false }: GameOverProps) {
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
      <span style={textStyle}>
        Game Over.
      </span>
    </div>
  );
}