from datetime import datetime, timezone
import uuid

from pydantic import EmailStr
from sqlmodel import JSON, Column, Field, SQLModel
import pgvector.sqlalchemy


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    full_name: str
    gender: str | None = None
    body_type: str | None = None
    skin_tone: str | None = None
    height_cm: str | None = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    initial_style_preferences: list[str] = []


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str


# Properties to receive via API on update, all are optional
class UserUpdate(SQLModel):
    full_name: str | None = None
    email: EmailStr | None = None
    body_type: str | None = None
    preferred_brands: list[str] | None = None


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))

    # --- Dynamic Analytics (Computed) ---
    style_scores: dict[str, float] = Field(default={}, sa_column=Column(JSON))

    # Finance & Spending DNA
    # Format: {"shoes": {"avg": 120.0, "max": 300.0}, "shirts": {"avg": 45.0}}
    spending_profile: dict[str, dict[str, float]] = Field(
        default={},
        sa_column=Column(JSON),
        description="Tracks category-specific budget limits and willingness to pay",
    )
    price_sensitivity_score: float = Field(
        default=0.5, description="0.0 (Budget/Thrift) to 1.0 (Luxury/High-End)"
    )

    # AI & Embeddings
    # This stores a vector representation of the user's taste for vector DB search

    style_embedding: list[float] | None = Field(
        default=None,
        sa_column=Column(pgvector.sqlalchemy.Vector(768)),
        description="Latent vector representing aesthetic preference for similarity matching",
    )

    # Behavioral Metrics
    return_rate: float = Field(
        default=0.0, description="Predicts purchase satisfaction"
    )
    last_active: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ProductBase(SQLModel):
    name: str = Field(index=True)
    brand: str = Field(index=True)
    master_category: str
    sub_category: str
    article_type: str
    gender: str
    mrp: float
    price: float

    # Stylist Context
    primary_colour: str
    fit: str | None = None
    material: str | None = None
    season: str | None = None


# --- DATABASE TABLES ---
class Product(ProductBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    # Data Science Signals
    rating: float = Field(default=0.0)
    rating_count: int = Field(default=0)
    is_fast_fashion: bool = False
    catalog_date: int

    # Relevance Engine (Stored as JSONB in Postgres for flexibility)
    occasion_tags: list[str] = Field(default=[], sa_column=Column(JSON))
    formality_score: float = Field(default=0.5)
    style_archetype: str | None = None

    # Content
    images: list[str] = Field(default=[], sa_column=Column(JSON))
    landing_page_url: str

    # 1. STYLE EMBEDDING (Visual & Aesthetic DNA)
    style_embedding: list[float] | None = Field(
        default=None, sa_column=Column(pgvector.sqlalchemy.Vector(512))
    )

    # 2. COMPLEMENTARY EMBEDDING (The "Stylist" Vector)
    complementary_embedding: list[float] | None = Field(
        default=None, sa_column=Column(pgvector.sqlalchemy.Vector(512))
    )

    # 3. TEXTUAL SEMANTIC EMBEDDING
    semantic_embedding: list[float] | None = Field(
        default=None, sa_column=Column(pgvector.sqlalchemy.Vector(384))
    )


class Inventory(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    product_id: uuid.UUID = Field(foreign_key="product.id")
    sku_id: int = Field(index=True)
    size: str
    stock_count: int
    available: bool = True


# --- API SCHEMAS ---
class ProductCreate(ProductBase):
    # What we require from the seller/onboarding
    id: uuid.UUID | None
    images: list[str] = Field(default=[], sa_column=Column(JSON))
    landing_page_url: str
    catalog_date: int


class ProductPublic(ProductBase):
    # What the user sees
    id: uuid.UUID
    rating: float
    occasion_tags: list[str]
    images: list[str]
    formality_score: float
    is_in_stock: bool = True  # Computed property


# Properties to receive on item update
class ProductUpdate(ProductBase):
    title: str | None = Field(
        default=None, min_length=1, max_length=255)  # type: ignore


class ProductsPublic(SQLModel):
    data: list[ProductPublic]
    count: int


class ProductCompatibility(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    base_product_id: uuid.UUID = Field(foreign_key="product.id", index=True)
    recommended_product_id: uuid.UUID = Field(foreign_key="product.id")

    # Pre-computed score (0.0 to 1.0)
    compatibility_score: float

    # Context (e.g., "This top goes with this bottom for a Wedding")
    occasion_context: str


class OutfitResponse(SQLModel):
    base: ProductPublic
    bottom: ProductPublic
    shoe: ProductPublic
    accessory: ProductPublic


class PersonalizedOutfits(SQLModel):
    outfits: list[OutfitResponse]


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)
