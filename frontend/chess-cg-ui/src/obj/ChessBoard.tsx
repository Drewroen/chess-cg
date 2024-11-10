export class ChessBoard {
  squares: (ChessPiece | null)[][];
  constructor(squares: (ChessPiece | null)[][]) {
    this.squares = squares;
  }
}
export class ChessPiece {
  type: string;
  color: string;

  constructor(type: string, color: string) {
    this.type = type;
    this.color = color;
  }
}
