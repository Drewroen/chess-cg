import React from "react";

export function Events({ events }: { events: unknown[] }) {
  return (
    <ul>
      {events.map((event, index) => (
        <li key={index}>{event as string}</li>
      ))}
    </ul>
  );
}
