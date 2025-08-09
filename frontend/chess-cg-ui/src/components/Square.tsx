import { CSSProperties } from "react";

export function Square({
  light,
  style,
}: {
  light: boolean;
  style: CSSProperties;
}) {
  return (
    <div
      style={{
        ...style,
        backgroundColor: light ? "#e8eaec" : "#798495",
      }}
    />
  );
}
