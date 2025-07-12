from uuid import UUID, uuid4
from app.obj.game import Game


class Room:
    def __init__(self):
        self.id = uuid4()
        self.white = None
        self.black = None
        self.game = Game()

    def open(self):
        return self.white is None or self.black is None

    def join(self, player: int) -> bool:
        if self.white is None:
            self.white = player
        elif self.black is None:
            self.black = player
        else:
            return False
        return True


class RoomService:
    def __init__(self):
        self.rooms = {}
        self.id_to_room_map = {}

    def add(self, websocket_id: int) -> UUID:
        for room in self.rooms.values():
            if room.open():
                room.join(websocket_id)
                self.id_to_room_map[websocket_id] = room
                return room.id
        new_room = Room()
        new_room.join(websocket_id)
        self.rooms[new_room.id] = new_room
        self.id_to_room_map[websocket_id] = new_room
        return new_room.id

    def get_player_room(self, player_id: int) -> Room:
        room = self.id_to_room_map.get(player_id)
        return room

    def get_room(self, room_id: str) -> Room:
        return self.rooms.get(room_id)
