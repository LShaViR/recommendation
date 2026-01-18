import uuid
from typing import List
from sqlmodel import Field, SQLModel, Column, Relationship, create_engine, Session
from pgvector.sqlalchemy import Vector
from sqlalchemy import text


class ProductTag(SQLModel, table=True):
    product_id: str = Field(foreign_key="product.id", primary_key=True)
    tag_id: str = Field(foreign_key="tag.id", primary_key=True)


class ProductImage(SQLModel, table=True):
    id: str = Field(primary_key=True)
    product_id: str = Field(foreign_key="product.id")
    image_url: str


class Tag(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str
    description: str

    products: List["Product"] = Relationship(
        back_populates="tags", link_model=ProductTag
    )


class Occassion(SQLModel, table=True):
    name: str = Field(primary_key=True)
    vector: List[float] = Field(sa_column=Column(Vector(768)))


class Style(SQLModel, table=True):
    name: str = Field(primary_key=True)
    vector: List[float] = Field(sa_column=Column(Vector(768)))


class Season(SQLModel, table=True):
    name: str = Field(primary_key=True)
    vector: List[float] = Field(sa_column=Column(Vector(768)))


class ColorComplementary(SQLModel, table=True):
    color_name: str = Field(foreign_key="color.name", primary_key=True)
    complementary_color_name: str = Field(foreign_key="color.name", primary_key=True)


class Color(SQLModel, table=True):
    name: str = Field(primary_key=True)
    vector: List[float] = Field(sa_column=Column(Vector(384)))

    complemantary_colors: List["Color"] = Relationship(
        back_populates="complementaries", link_model=ColorComplementary
    )


class UserBase(SQLModel):
    name: str
    email: str
    budget: int = Field(default=0)
    password: str


class User(UserBase, table=True):
    id: str = Field(primary_key=True)
    products: List["Product"] = Relationship(back_populates="user")


class UserLogin(SQLModel):
    email: str
    password: str


class UserCreate(UserBase):
    pass


class ProductBase(SQLModel):
    sku_id: str = Field(unique=True)
    title: str
    description: str
    sector: str
    price: int
    brand_name: str
    product_type: str = Field(index=True)
    gender: str = Field(index=True)
    occasion: str = Field(index=True, foreign_key="occasion.name")
    season: str = Field(index=True, foreign_key="season.name")
    primary_color: str = Field(index=True, foreign_key="color.name")


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class Product(ProductBase, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)

    occasion_vector: List[float] = Field(sa_column=Column(Vector(768)))
    style_vector: List[float] = Field(sa_column=Column(Vector(768)))
    color_vector: List[float] = Field(sa_column=Column(Vector(768)))
    overall_vector: List[float] = Field(sa_column=Column(Vector(768)))

    user: User = Relationship(back_populates="products")
    tags: List["Tag"] = Relationship(back_populates="products", link_model=ProductTag)
    images: List["ProductImage"] = Relationship(back_populates="product")


postgres_file_name = "culture_circle"
postgres_url = f"postgresql://postgres:postgres@localhost:5432/{postgres_file_name}"

connect_args = {}
engine = create_engine(postgres_url, connect_args=connect_args)


def create_db_and_tables() -> None:
    with engine.connect() as conn:
        # This MUST happen before creating tables with Vector columns
        print("Creating database and tables...")
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    SQLModel.metadata.create_all(engine)

    print("Database and tables created successfully.")


def get_session() -> Session:
    with Session(engine) as session:
        yield session
