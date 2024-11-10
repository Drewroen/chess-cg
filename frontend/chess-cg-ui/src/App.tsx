import React, { useState, useEffect } from "react";
import { socket } from "./socket";
import { ConnectionState } from "./components/ConnectionState";
import { ConnectionManager } from "./components/ConnectionManager";
import { Events } from "./components/Events";

export default function App() {
  const [isConnected, setIsConnected] = useState(socket.connected);
  const [fooEvents, setFooEvents] = useState<unknown[]>([]);

  useEffect(() => {
    function onConnect() {
      console.log("BBBBB");
      setIsConnected(true);
    }

    function onNewConnect(data: unknown) {
      console.log("GOT THIS MESSAGE");
      setFooEvents((prev) => [...prev, data]);
    }

    function onNewDisconnect(data: unknown) {
      console.log("GOT THIS MESSAGE");
      setFooEvents((prev) => prev.filter((e) => e !== data));
    }

    function onDisconnect() {
      console.log("AAAAA");
      setIsConnected(false);
      setFooEvents([]);
    }

    socket.on("newConnection", (data) => onNewConnect(data));
    socket.on("newDisconnection", (data) => onNewDisconnect(data));
    socket.on("connect", onConnect);
    socket.on("disconnect", onDisconnect);

    return () => {
      socket.off("connect");
      socket.off("newConnection");
      socket.off("disconnect");
      socket.off("newDisconnection");
    };
  }, []);

  return (
    <div className="App">
      <ConnectionState isConnected={isConnected} />
      <Events events={fooEvents} />
      <ConnectionManager />
    </div>
  );
}
