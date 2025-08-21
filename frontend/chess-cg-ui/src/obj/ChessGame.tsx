export class ChessBoard {
  squares?: (ChessPiece | null)[][];
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
  winner?: string;
  time: RemainingTime = new RemainingTime();
  moves: ChessMove[] = []; // Simplified - now just one array based on turn
  opponentConnected: boolean = false; // New field for opponent connection status
  id: string = ""; // Room ID for fetching game info
  playerId: string = ""; // Player ID to identify which player this is
}
export class ChessPlayers {
  white: { id: number; name: string; connected: boolean; elo?: number } = {
    id: -1,
    name: "Disconnected",
    connected: false,
  };
  black: { id: number; name: string; connected: boolean; elo?: number } = {
    id: -1,
    name: "Disconnected",
    connected: false,
  };
}

export class KingsInCheck {
  white: boolean = false;
  black: boolean = false;
}

export interface ChessMove {
  from: { row: number; col: number };
  to: { row: number; col: number };
}

export interface Move {
  from: [number, number];
  to: [number, number];
}

export class ChessMoves {
  white: ChessMove[] = [];
  black: ChessMove[] = [];
}

export class RemainingTime {
  white: number = 0;
  black: number = 0;
}

export class BoardEvent {
  squares: ChessPiece[][] = [];
  turn: string = "white";
  kings_in_check: KingsInCheck = new KingsInCheck();
  status: string = "";
  winner?: string;
  time: RemainingTime = { white: 0, black: 0 };
  moves: ChessMove[] = []; // Simplified - turn-based moves/premoves
  opponent_connected: boolean = false; // New field for opponent connection
  id: string = ""; // Room ID for fetching game info
  player_id: string = ""; // Player ID to identify which player this is
}

export interface MoveMessage {
  type: "move";
  from: [number, number];
  to: [number, number];
  promotion?: string;
}

export interface ResetPremoveMessage {
  type: "reset_premove";
}

export type WebSocketMessage = MoveMessage | ResetPremoveMessage;
