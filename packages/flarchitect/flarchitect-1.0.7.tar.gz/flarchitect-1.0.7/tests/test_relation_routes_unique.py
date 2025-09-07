from __future__ import annotations

from typing import Any

from flask import Flask
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

from flarchitect.core.architect import Architect


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    class Meta:
        tag_group = "Test"
        tag = "Users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)


class Friend(Base):
    __tablename__ = "friends"

    class Meta:
        tag_group = "Test"
        tag = "Friends"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    friend_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    # Two relationships to the same target model with distinct keys
    user: Mapped[User] = relationship(User, foreign_keys=[user_id])
    friend: Mapped[User] = relationship(User, foreign_keys=[friend_id])


def _make_app(rel_style: str = "relation-key") -> tuple[Flask, Session]:
    app = Flask(__name__)
    app.config.update(
        {
            "TESTING": True,
            "FULL_AUTO": True,
            "API_BASE_MODEL": Base,
            # Ensure relations are generated and use the chosen style
            "API_ADD_RELATIONS": True,
            "API_RELATION_URL_STYLE": rel_style,
            # Trim overhead in tests
            "API_CREATE_DOCS": True,
        }
    )

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)

    # Seed data
    from sqlalchemy.orm import sessionmaker

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    u1 = User(name="Alice")
    u2 = User(name="Bob")
    session.add_all([u1, u2])
    session.flush()
    f = Friend(user_id=u1.id, friend_id=u2.id)
    session.add(f)
    session.commit()

    Architect(app)  # auto-initialises and registers routes/spec
    return app, session


def test_relation_routes_use_relation_key_segment() -> None:
    app, _ = _make_app(rel_style="relation-key")
    client = app.test_client()

    # Expect distinct endpoints per relation key
    r1 = client.get("/api/friends/1/user")
    r2 = client.get("/api/friends/1/friend")

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.get_json()["value"]["name"] == "Alice"
    assert r2.get_json()["value"]["name"] == "Bob"

    # OpenAPI should include both relation endpoints
    spec = client.get("/docs/apispec.json").get_json()
    paths: dict[str, Any] = spec.get("paths", {})
    assert any(p.endswith("/friends/{id}/user") for p in paths)
    assert any(p.endswith("/friends/{id}/friend") for p in paths)


def test_relation_routes_target_model_style_backcompat() -> None:
    app, _ = _make_app(rel_style="target-model")
    client = app.test_client()

    # Old behaviour uses target model endpoint as final segment
    r = client.get("/api/friends/1/users")
    assert r.status_code == 200
    assert r.get_json()["value"]["name"] == "Alice"

    # Ensure joins still operate (no exception) on the base model
    q = client.get("/api/friends?join=user,friend")
    assert q.status_code == 200
