const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";

export interface GameInfo {
  room_id: string;
  players: {
    white: {
      id: string;
      name: string;
      elo: number | null;
    };
    black: {
      id: string;
      name: string;
      elo: number | null;
    };
  };
}

export async function fetchGameInfo(roomId: string): Promise<GameInfo> {
  const response = await fetch(`${BACKEND_URL}/api/game/${roomId}/info`, {
    method: "GET",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch game info: ${response.statusText}`);
  }

  return response.json();
}