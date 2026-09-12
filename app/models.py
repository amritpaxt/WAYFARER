from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    character: Mapped["Character"] = relationship(back_populates="user", cascade="all, delete-orphan", uselist=False)
    quests: Mapped[list["Quest"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    unlocked_fragments: Mapped[list["UnlockedFragment"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    inventory: Mapped[list["InventoryItem"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Character(Base):
    __tablename__ = "characters"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    level: Mapped[int] = mapped_column(Integer, default=1)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    resource_meter: Mapped[int] = mapped_column(Integer, default=100)
    gold: Mapped[int] = mapped_column(Integer, default=0)
    last_login_date: Mapped[date] = mapped_column(Date, default=date.today)
    user: Mapped[User] = relationship(back_populates="character")
    stats: Mapped[list["Stat"]] = relationship(back_populates="character", cascade="all, delete-orphan")


class Stat(Base):
    __tablename__ = "stats"
    id: Mapped[int] = mapped_column(primary_key=True)
    character_id: Mapped[int] = mapped_column(ForeignKey("characters.id"))
    name: Mapped[str] = mapped_column(String(32))
    value: Mapped[int] = mapped_column(Integer, default=0)
    character: Mapped[Character] = relationship(back_populates="stats")


class Quest(Base):
    __tablename__ = "quests"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(64))
    difficulty: Mapped[str] = mapped_column(String(16))
    is_final_vow: Mapped[bool] = mapped_column(Boolean, default=False)
    xp_reward: Mapped[int] = mapped_column(Integer)
    gold_reward: Mapped[int] = mapped_column(Integer)
    resource_reward: Mapped[int] = mapped_column(Integer)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    user: Mapped[User] = relationship(back_populates="quests")


class Episode(Base):
    __tablename__ = "episodes"
    id: Mapped[int] = mapped_column(primary_key=True)
    day_number: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(120))
    fragments_normal: Mapped[list[str]] = mapped_column(JSON)
    fragments_hard: Mapped[list[str]] = mapped_column(JSON)
    reveal_normal: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reveal_hard: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    unlock_resource_threshold: Mapped[int] = mapped_column(Integer, default=35)
    unlocked_fragments: Mapped[list["UnlockedFragment"]] = relationship(back_populates="episode")


class UnlockedFragment(Base):
    __tablename__ = "unlocked_fragments"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    episode_id: Mapped[int] = mapped_column(ForeignKey("episodes.id"))
    fragment_index: Mapped[int] = mapped_column(Integer)
    variant_shown: Mapped[str] = mapped_column(String(10))
    unlocked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user: Mapped[User] = relationship(back_populates="unlocked_fragments")
    episode: Mapped[Episode] = relationship(back_populates="unlocked_fragments")


class ShopItem(Base):
    __tablename__ = "shop_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    cost: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text)


class InventoryItem(Base):
    __tablename__ = "inventory_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    shop_item_id: Mapped[int] = mapped_column(ForeignKey("shop_items.id"))
    user: Mapped[User] = relationship(back_populates="inventory")
