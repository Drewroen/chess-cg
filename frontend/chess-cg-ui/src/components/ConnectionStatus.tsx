import React from "react";

interface ConnectionStatusProps {
  connected: boolean;
  username?: string;
}

export function ConnectionStatus({
  connected,
  username = "Guest",
}: ConnectionStatusProps) {
  const getStatusColor = () => {
    if (connected) return "#22c55e";
    return "#6b7280";
  };

  return (
    <div
      style={{
        width: 200,
        height: 48,
        border: "1px solid #e5e7eb",
        borderRadius: 4,
        fontSize: 20,
        fontWeight: 200,
        display: "flex",
        alignItems: "center",
        justifyContent: "left",
        gap: 12,
        boxShadow: "0 1px 3px rgba(0, 0, 0, 0.1)",
        color: "#374151",
      }}
    >
      <div
        style={{
          width: 12,
          height: 12,
          borderRadius: "50%",
          backgroundColor: getStatusColor(),
          flexShrink: 0,
          marginLeft: 10,
        }}
      />
      <span
        style={{
          lineHeight: 1,
          margin: 0,
          padding: 0,
          color: "white",
          fontWeight: 100,
          fontFamily: "sans-serif",
        }}
      >
        {username}
      </span>
    </div>
  );
}
