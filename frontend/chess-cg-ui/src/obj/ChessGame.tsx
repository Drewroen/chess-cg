export class ChessBoard {
  squares?: ChessPiece[][];
  constructor(squares?: ChessPiece[][]) {
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

export class ChessGame {
  board?: ChessBoard = new ChessBoard();
  possibleMoves?: Array<[number, number]> = [];
}