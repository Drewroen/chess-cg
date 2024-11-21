import LightSquare from "../assets/light_square.svg";
import DarkSquare from "../assets/dark_square.svg";
import { CSSProperties } from "react";

export function Square({
  light,
  style,
}: {
  light: boolean;
  style: CSSProperties;
}) {
  return <img src={light ? LightSquare : DarkSquare} style={style} alt="" />;
}
