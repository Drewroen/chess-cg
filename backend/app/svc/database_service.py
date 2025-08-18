from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db_models import User, ChessGame
from typing import Optional
from uuid import uuid4


class DatabaseService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user_data: dict) -> User:
        # Set ELO based on user type
        if user_data.get("user_type") == "authenticated":
            user_data["elo"] = 1200
        elif user_data.get("user_type") == "guest":
            user_data["elo"] = None
        
        user = User(**user_data)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def create_guest_user(self, guest_id: str, name: str = "Guest") -> User:
        guest_data = {
            "id": guest_id,
            "name": "Guest",
            "username": name,
            "user_type": "guest",
        }
        return await self.create_user(guest_data)

    async def get_guest_users(self) -> list[User]:
        result = await self.session.execute(
            select(User).where(User.user_type == "guest")
        )
        return result.scalars().all()

    async def create_chess_game(self, white_player_id: str, black_player_id: str, winner: str = None) -> ChessGame:
        game_data = {
            "id": str(uuid4()),
            "white_player_id": white_player_id,
            "black_player_id": black_player_id,
            "winner": winner
        }
        chess_game = ChessGame(**game_data)
        self.session.add(chess_game)
        await self.session.commit()
        await self.session.refresh(chess_game)
        return chess_game
