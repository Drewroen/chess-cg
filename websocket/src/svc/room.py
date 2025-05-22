from uuid import UUID
from obj.room import Room
from flask_socketio import join_room


class RoomService:
    def __init__(self):
        self.rooms = {}
        self.id_to_room_map = {}

    def add(self, websocket_id: str) -> UUID:
        for room in self.rooms.values():
            if room.open():
                room.join(websocket_id)
                join_room(room.id)
                self.id_to_room_map[websocket_id] = room
                return room.id
        new_room = Room()
        new_room.join(websocket_id)
        join_room(new_room.id)
        self.rooms[new_room.id] = new_room
        self.id_to_room_map[websocket_id] = new_room
        return new_room.id

    def get_player_room(self, player_id: int) -> Room:
        room = self.id_to_room_map.get(player_id)
        return room

    def get_room(self, room_id: str) -> Room:
        return self.rooms.get(room_id)
