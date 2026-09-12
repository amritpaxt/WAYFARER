from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Credentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class QuestCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    category: str
    difficulty: str


class QuestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    category: str
    difficulty: str
    is_completed: bool
    xp_reward: int
    gold_reward: int
    resource_reward: int
    created_at: datetime
    completed_at: datetime | None
    story_day: int | None


class CharacterOut(BaseModel):
    id: int
    level: int
    xp: int
    xp_to_next_level: int
    resource_meter: int
    gold: int
    day_index: int
    last_login_date: date
    stats: dict[str, int]


class ShopItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    cost: int
    description: str


class InventoryItemOut(BaseModel):
    id: int
    shop_item_id: int
    name: str
    description: str


class PurchaseOut(BaseModel):
    character: CharacterOut
    inventory: list[InventoryItemOut]
