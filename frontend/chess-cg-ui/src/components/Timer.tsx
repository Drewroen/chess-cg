import React, { useState, useEffect, useRef } from "react";
import styles from "./Timer.module.css";

interface TimerProps {
  initialTime: number;
  isActive: boolean;
  isMobile?: boolean;
}

export const Timer: React.FC<TimerProps> = ({
  initialTime,
  isActive,
  isMobile = false,
}) => {
  const [timeRemaining, setTimeRemaining] = useState(initialTime);
  const startTimeRef = useRef<number | null>(null);
  const initialTimeRef = useRef(initialTime);

  useEffect(() => {
    setTimeRemaining(initialTime);
    initialTimeRef.current = initialTime;
    if (isActive) {
      startTimeRef.current = Date.now();
    }
  }, [initialTime, isActive]);

  useEffect(() => {
    let animationFrame: number | null = null;

    const updateTimer = () => {
      if (!isActive || !startTimeRef.current) return;

      const elapsed = (Date.now() - startTimeRef.current) / 1000;
      const remaining = Math.max(0, initialTimeRef.current - elapsed);
      setTimeRemaining(remaining);

      if (remaining > 0) {
        animationFrame = requestAnimationFrame(updateTimer);
      }
    };

    const handleVisibilityChange = () => {
      if (document.hidden) {
        if (animationFrame) {
          cancelAnimationFrame(animationFrame);
          animationFrame = null;
        }
      } else if (isActive && timeRemaining > 0) {
        updateTimer();
      }
    };

    if (isActive && timeRemaining > 0) {
      if (!startTimeRef.current) {
        startTimeRef.current = Date.now();
      }

      updateTimer();
      document.addEventListener("visibilitychange", handleVisibilityChange);
    } else {
      startTimeRef.current = null;
    }

    return () => {
      if (animationFrame) {
        cancelAnimationFrame(animationFrame);
      }
      document.removeEventListener("visibilitychange", handleVisibilityChange);
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
      className={`${styles.timerContainer} ${
        isMobile ? styles.timerContainerMobile : styles.timerContainerDesktop
      }`}
    >
      <div className={styles.timerText}>
        {formatTime(timeRemaining)}
      </div>
    </div>
  );
};
