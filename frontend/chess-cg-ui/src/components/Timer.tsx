import React, { useState, useEffect, useRef } from "react";
import styles from "./Timer.module.css";
import { formatTime } from "../utils";

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
