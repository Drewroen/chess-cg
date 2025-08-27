import { ReactNode, ButtonHTMLAttributes } from "react";

export type ButtonVariant = "primary" | "secondary" | "danger" | "neutral";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  children: ReactNode;
  isLoading?: boolean;
  isMobile?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  variant = "primary",
  children,
  isLoading = false,
  isMobile = false,
  disabled,
  ...props
}) => {
  const baseStyles: React.CSSProperties = {
    padding: isMobile ? "0.875rem 1.5rem" : "1rem 2rem",
    fontSize: isMobile ? "0.9rem" : "1rem",
    fontWeight: variant === "primary" ? "600" : "500",
    borderRadius: "8px",
    cursor: (disabled || isLoading) ? "not-allowed" : "pointer",
    transition: "all 0.2s ease",
    fontFamily: "inherit",
    opacity: (disabled || isLoading) ? 0.7 : 1,
  };

  const variantStyles: Record<ButtonVariant, React.CSSProperties> = {
    primary: {
      border: "none",
      background: isLoading
        ? "linear-gradient(145deg, #cccccc, #aaaaaa)"
        : "linear-gradient(145deg, #ffffff, #e0e0e0)",
      color: "#1a1a1a",
      boxShadow:
        "0 4px 12px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.8)",
    },
    secondary: {
      border: "2px solid #4CAF50",
      background: "transparent",
      color: "#4CAF50",
    },
    danger: {
      border: "2px solid #f44336",
      background: "transparent",
      color: "#f44336",
    },
    neutral: {
      border: "2px solid #505050",
      background: "transparent",
      color: "#a0a0a0",
    },
  };

  const handleMouseOver = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (disabled || isLoading) return;

    const target = e.currentTarget;
    target.style.transform = "translateY(-1px)";

    switch (variant) {
      case "primary":
        target.style.boxShadow =
          "0 6px 16px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.8)";
        break;
      case "secondary":
        target.style.background = "#4CAF50";
        target.style.color = "#ffffff";
        break;
      case "danger":
        target.style.background = "#f44336";
        target.style.color = "#ffffff";
        break;
      case "neutral":
        target.style.background = "#505050";
        target.style.color = "#f0f0f0";
        target.style.borderColor = "#606060";
        break;
    }
  };

  const handleMouseOut = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (disabled || isLoading) return;

    const target = e.currentTarget;
    target.style.transform = "translateY(0)";

    switch (variant) {
      case "primary":
        target.style.boxShadow =
          "0 4px 12px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.8)";
        break;
      case "secondary":
        target.style.background = "transparent";
        target.style.color = "#4CAF50";
        break;
      case "danger":
        target.style.background = "transparent";
        target.style.color = "#f44336";
        break;
      case "neutral":
        target.style.background = "transparent";
        target.style.color = "#a0a0a0";
        target.style.borderColor = "#505050";
        break;
    }
  };

  return (
    <button
      {...props}
      disabled={disabled || isLoading}
      style={{
        ...baseStyles,
        ...variantStyles[variant],
        ...props.style,
      }}
      onMouseOver={handleMouseOver}
      onMouseOut={handleMouseOut}
    >
      {isLoading && variant === "primary" ? "Loading..." : children}
    </button>
  );
};