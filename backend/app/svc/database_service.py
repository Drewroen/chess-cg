from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db_models import User, ChessGame, RefreshToken
from typing import Optional
from uuid import uuid4
from datetime import datetime, timezone


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

    async def update_user_username(self, user_id: str, username: str) -> Optional[User]:
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        # Check if username is already taken by another user
        existing_user = await self.get_user_by_username(username)
        if existing_user and existing_user.id != user_id:
            return None  # Username already taken

        user.username = username
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_user_elo(self, user_id: str, new_elo: int) -> Optional[User]:
        """Update a user's ELO rating."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        user.elo = new_elo
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def create_chess_game(
        self,
        white_player_id: str,
        black_player_id: str,
        winner: str = None,
        end_reason: str = None,
    ) -> ChessGame:
        game_data = {
            "id": str(uuid4()),
            "white_player_id": white_player_id,
            "black_player_id": black_player_id,
            "winner": winner,
            "end_reason": end_reason,
        }
        chess_game = ChessGame(**game_data)
        self.session.add(chess_game)
        await self.session.commit()
        await self.session.refresh(chess_game)
        return chess_game

    async def create_refresh_token(self, token_data: dict) -> RefreshToken:
        """Create a new refresh token in the database"""
        refresh_token_obj = RefreshToken(**token_data)
        self.session.add(refresh_token_obj)
        await self.session.commit()
        await self.session.refresh(refresh_token_obj)
        return refresh_token_obj

    async def get_refresh_token(self, token: str) -> Optional[RefreshToken]:
        """Get refresh token by token string"""
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.token == token)
        )
        return result.scalar_one_or_none()

    async def update_refresh_token(self, token_obj: RefreshToken) -> RefreshToken:
        """Update refresh token data"""
        await self.session.commit()
        await self.session.refresh(token_obj)
        return token_obj

    async def delete_refresh_token(self, token_obj: RefreshToken) -> bool:
        """Delete a refresh token"""
        await self.session.delete(token_obj)
        await self.session.commit()
        return True

    async def cleanup_expired_refresh_tokens(self) -> int:
        """Remove expired refresh tokens from storage"""
        current_time = datetime.now(timezone.utc).replace(tzinfo=None)
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.expires_at < current_time)
        )
        expired_tokens = result.scalars().all()

        count = len(expired_tokens)
        for token in expired_tokens:
            await self.session.delete(token)

        await self.session.commit()
        return count
