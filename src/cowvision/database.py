from __future__ import annotations

"""Infraestrutura de acesso ao banco.

Centraliza engine, fabrica de sessoes e um context manager para operacoes
curtas de leitura e escrita usando SQLAlchemy.
"""

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from cowvision.config import settings


engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    """Classe base para todos os modelos ORM."""

    pass


@contextmanager
def session_scope() -> Session:
    """Abre uma sessao transacional curta.

    Uso:
    - entra com uma sessao pronta para uso
    - faz commit se tudo der certo
    - faz rollback em caso de erro
    """

    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
