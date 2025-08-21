interface DrawResignButtonsProps {
  isMobile?: boolean;
}

export function DrawResignButtons({ isMobile = false }: DrawResignButtonsProps) {
  const buttonStyle = {
    padding: "8px 16px",
    backgroundColor: "transparent",
    color: "#888",
    border: "1px solid #555",
    borderRadius: "6px",
    cursor: "pointer",
    fontSize: "14px",
    display: "flex",
    alignItems: "center",
    gap: "4px",
  } as const;

  const containerStyle = isMobile 
    ? {
        display: "flex",
        justifyContent: "center",
        gap: "16px",
        margin: "12px 0",
        width: "100%",
        maxWidth: "600px",
        boxSizing: "border-box" as const,
      }
    : {
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        gap: "8px",
        padding: "16px 0",
      };

  return (
    <div style={containerStyle}>
      <button style={buttonStyle} title="Offer draw">
        ½
      </button>
      <button style={buttonStyle} title="Resign">
        ⚐
      </button>
    </div>
  );
}