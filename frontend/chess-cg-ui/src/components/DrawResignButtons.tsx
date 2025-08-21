interface DrawResignButtonsProps {
  isMobile?: boolean;
  socket?: WebSocket | null;
  drawRequests?: { white: boolean; black: boolean };
  playerColor?: "white" | "black";
}

export function DrawResignButtons({ 
  isMobile = false, 
  socket, 
  drawRequests = { white: false, black: false },
  playerColor = "white"
}: DrawResignButtonsProps) {
  const handleResign = () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ type: "resign" }));
    }
  };

  const handleDrawRequest = () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ type: "request_draw" }));
    }
  };

  const opponentDrawRequested = drawRequests[playerColor === "white" ? "black" : "white"];
  const playerDrawRequested = drawRequests[playerColor];

  const getDrawButtonStyle = () => {
    let backgroundColor = "transparent";
    let color = "#888";
    let border = "1px solid #555";
    
    if (opponentDrawRequested && !playerDrawRequested) {
      // Opponent has requested a draw - highlight to accept
      backgroundColor = "#4CAF50";
      color = "#fff";
      border = "1px solid #4CAF50";
    } else if (playerDrawRequested) {
      // Player has requested a draw - show as pending
      backgroundColor = "#FFA726";
      color = "#fff";
      border = "1px solid #FFA726";
    }
    
    return {
      padding: "8px 16px",
      backgroundColor,
      color,
      border,
      borderRadius: "6px",
      cursor: "pointer",
      fontSize: "14px",
      display: "flex",
      alignItems: "center",
      gap: "4px",
    } as const;
  };

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

  const getDrawButtonTitle = () => {
    if (opponentDrawRequested && !playerDrawRequested) {
      return "Accept draw offer";
    } else if (playerDrawRequested) {
      return "Draw offered (waiting for opponent)";
    } else {
      return "Offer draw";
    }
  };

  return (
    <div style={containerStyle}>
      <button 
        style={getDrawButtonStyle()} 
        title={getDrawButtonTitle()}
        onClick={handleDrawRequest}
      >
        ½
      </button>
      <button style={buttonStyle} title="Resign" onClick={handleResign}>
        ⚐
      </button>
    </div>
  );
}