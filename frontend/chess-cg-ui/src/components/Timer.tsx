import React, { useState, useEffect } from "react";

interface TimerProps {
  initialTime: number;
  isActive: boolean;
}

export const Timer: React.FC<TimerProps> = ({ initialTime, isActive }) => {
  const [timeRemaining, setTimeRemaining] = useState(initialTime);

  useEffect(() => {
    setTimeRemaining(initialTime);
  }, [initialTime]);

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;

    if (isActive && timeRemaining > 0) {
      interval = setInterval(() => {
        setTimeRemaining((prevTime) => (prevTime <= 0.1 ? 0 : prevTime - 0.1));
      }, 100);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isActive, timeRemaining]);

  const formatTime = (seconds: number): string => {
    const total = Math.max(0, seconds);
    const hours = Math.floor(total / 3600);
    const minutes = Math.floor((total % 3600) / 60);
    const secs = total % 60;

    const mm = minutes.toString().padStart(2, "0");
    const ss = secs.toFixed(1).padStart(4, "0");

    return hours > 0 ? `${hours}:${mm}:${ss}` : `${mm}:${ss}`;
  };

  return (
    <div
      style={{
        width: 200,
        height: 48,
        border: "1px solid #e5e7eb",
        borderRadius: 4,
        fontSize: 36,
        fontWeight: 200,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: 12,
        boxShadow: "0 1px 3px rgba(0, 0, 0, 0.1)",
        color: "#374151",
      }}
    >
      <div
        style={{
          lineHeight: 1,
          margin: 0,
          padding: 0,
          color: "white",
          fontWeight: 100,
          fontFamily: "sans-serif",
        }}
      >
        {formatTime(timeRemaining)}
      </div>
    </div>
  );
};
