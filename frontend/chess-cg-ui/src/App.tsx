import { useState, useEffect } from "react";
import { socket } from "./socket";
import { ChessBoard } from "./obj/ChessBoard";
import { Board } from "./components/Board";

export default function App() {
  const [isConnected, setIsConnected] = useState(socket.connected);
  const [chessBoard, setChessBoard] = useState<ChessBoard | undefined>(
    undefined
  );

  useEffect(() => {
    function onConnect() {
      setIsConnected(true);
    }

    function onDisconnect() {
      setIsConnected(false);
      setChessBoard(undefined);
    }

    function onBoard(data: ChessBoard) {
      setChessBoard(data);
    }

    function onTileClick(data: any) {
      console.log("Tile clicked", data);
    }

    socket.on("connect", onConnect);
    socket.on("disconnect", onDisconnect);
    socket.on("board", onBoard);
    socket.on("tileClick", onTileClick);

    return () => {
      socket.off("connect");
      socket.off("disconnect");
      socket.off("board");
      socket.off("tileClick");
    };
  }, []);

  return (
    <div className="App">{isConnected && <Board board={chessBoard} />}</div>
  );
}
