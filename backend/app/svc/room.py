from uuid import UUID, uuid4
from app.obj.game import Game


class Room:
    def __init__(self):
        self.id = uuid4()
        self.white: int = None
        self.black: int = None
        self.game: Game = Game()

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

    def leave(self, player: int) -> bool:
        if self.white == player:
            self.white = None
            return True
        elif self.black == player:
            self.black = None
            return True
        return False

    def player_color(self, player: int) -> bool:
        return (
            "white"
            if self.white == player
            else "black"
            if self.black == player
            else None
        )


class RoomService:
    def __init__(self):
        self.rooms: dict[int, Room] = {}
        self.id_to_room_map: dict[int, Room] = {}

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
        return self.id_to_room_map.get(player_id)

    def get_room(self, room_id: str) -> Room:
        return self.rooms.get(room_id)

    def disconnect(self, player_id: int):
        room: Room = self.id_to_room_map.get(player_id)
        if room:
            room.leave(player_id)
            if room.game.status != "complete":
                color = room.player_color(player_id)
                if color:
                    room.game.mark_player_forfeit(color)
            if room.white is None and room.black is None:
                del self.rooms[room.id]
            del self.id_to_room_map[player_id]
