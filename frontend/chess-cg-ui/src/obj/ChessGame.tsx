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
  players?: ChessPlayers = new ChessPlayers();
  kingsInCheck?: KingsInCheck = new KingsInCheck();
  turn: string = "";
  status: string = "";
  time: RemainingTime = new RemainingTime();
}

export class ChessPlayers {
  white: string = "";
  black: string = "";
}

export class KingsInCheck {
  white: boolean = false;
  black: boolean = false;
}

export class RemainingTime {
  white: number = 0;
  black: number = 0;
}

export class BoardEvent {
  squares: ChessPiece[][] = [];
  players: ChessPlayers = new ChessPlayers();
  turn: string = "white";
  kings_in_check: KingsInCheck = new KingsInCheck();
  status: string = "";
  time: RemainingTime = { white: 0, black: 0 };
}
