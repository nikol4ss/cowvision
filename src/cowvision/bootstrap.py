from __future__ import annotations

from cowvision.database import Base, engine


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
