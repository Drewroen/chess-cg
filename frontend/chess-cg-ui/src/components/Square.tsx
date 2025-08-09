import { CSSProperties } from "react";

export function Square({
  light,
  style,
  premove = false,
}: {
  light: boolean;
  style: CSSProperties;
  premove?: boolean;
}) {
  return (
    <div
      style={{
        ...style,
        backgroundColor: light ? "#e8eaec" : "#798495",
      }}
    >
      {premove && (
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "#66918aD0",
            pointerEvents: "none",
          }}
        />
      )}
    </div>
  );
}
