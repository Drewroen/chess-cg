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
        width: 250,
        border: "1px solid #ccc",
        borderRadius: 4,
        padding: 8,
        fontFamily: "sans-serif",
        boxSizing: "border-box",
        textAlign: "center",
        fontSize: 40,
        fontWeight: "100",
      }}
    >
      <div>{formatTime(timeRemaining)}</div>
    </div>
  );
};
