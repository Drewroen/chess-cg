import { useState, useEffect } from "react";
import { socket } from "./socket";
import { ChessBoard } from "./obj/ChessBoard";
import { Board } from "./components/Board";

export default function App() {
  const [isConnected, setIsConnected] = useState(socket.connected);
  const [chessBoard, setChessBoard] = useState<ChessBoard | undefined>(
    undefined
  );
  const [coord1, setCoord1] = useState("");
  const [coord2, setCoord2] = useState("");

  useEffect(() => {
    function onConnect() {
      console.log("BBBBB");
      setIsConnected(true);
    }

    function onDisconnect() {
      setIsConnected(false);
      setChessBoard(undefined);
    }

    function onBoard(data: ChessBoard) {
      setChessBoard(data);
    }

    socket.on("connect", onConnect);
    socket.on("disconnect", onDisconnect);
    socket.on("board", onBoard);

    return () => {
      socket.off("connect");
      socket.off("disconnect");
      socket.off("board");
    };
  }, []);

  return (
    <div className="App">
      {isConnected && <Board board={chessBoard} />}
      <input value={coord1} onChange={(e) => setCoord1(e.target.value)}></input>
      <input value={coord2} onChange={(e) => setCoord2(e.target.value)}></input>
      <button
        onClick={() =>
          socket.emit("move", {
            start: coord1,
            end: coord2,
          })
        }
      >
        Move
      </button>
    </div>
  );
}
