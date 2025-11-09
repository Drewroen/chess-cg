export class ChessBoard {
  squares?: (ChessPiece | null)[][];
  constructor(squares?: ChessPiece[][]) {
    this.squares = squares;
  }
}

export type PieceType = "pawn" | "rook" | "knight" | "bishop" | "queen" | "king";
export type PieceColor = "white" | "black";
export type GameStatus = "waiting" | "active" | "complete" | "not started" | "in progress" | "aborted";

export class ChessPiece {
  type: PieceType;
  color: PieceColor;
  modifiers?: { type: string; score: number; applicable_piece: string; description: string; uses: number }[];

  constructor(type: PieceType, color: PieceColor, modifiers?: { type: string; score: number; applicable_piece: string; description: string; uses: number }[]) {
    this.type = type;
    this.color = color;
    this.modifiers = modifiers;
  }
}

export class ChessGame {
  board?: ChessBoard = new ChessBoard();
  possibleMoves?: Array<[number, number]> = [];
  players?: ChessPlayers = new ChessPlayers();
  kingsInCheck?: KingsInCheck = new KingsInCheck();
  turn: PieceColor = "white";
  status: GameStatus = "not started";
  winner?: PieceColor;
  endReason?: string;
  time: RemainingTime = new RemainingTime();
  moves: ChessMove[] = []; // Simplified - now just one array based on turn
  opponentConnected: boolean = false; // New field for opponent connection status
  id: string = ""; // Room ID for fetching game info
  playerId: string = ""; // Player ID to identify which player this is
  drawRequests: { white: boolean; black: boolean } = { white: false, black: false };
  lastMove: ChessMove | null = null; // Last move made in the game
  capturedPieces: { white: ChessPiece[]; black: ChessPiece[] } = { white: [], black: [] };
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
  turn: PieceColor = "white";
  kings_in_check: KingsInCheck = new KingsInCheck();
  status: GameStatus = "not started";
  winner?: PieceColor;
  end_reason?: string;
  time: RemainingTime = { white: 0, black: 0 };
  moves: ChessMove[] = []; // Simplified - turn-based moves/premoves
  opponent_connected: boolean = false; // New field for opponent connection
  id: string = ""; // Room ID for fetching game info
  player_id: string = ""; // Player ID to identify which player this is
  draw_requests: { white: boolean; black: boolean } = { white: false, black: false };
  last_move: ChessMove | null = null; // Last move made in the game
  captured_pieces: { white: ChessPiece[]; black: ChessPiece[] } = { white: [], black: [] };
}

export interface MoveMessage {
  type: "move";
  from: [number, number];
  to: [number, number];
  promotion?: PieceType;
}

export interface ResetPremoveMessage {
  type: "reset_premove";
}

export type WebSocketMessage = MoveMessage | ResetPremoveMessage;
