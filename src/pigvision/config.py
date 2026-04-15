from __future__ import annotations

"""Configuracoes centrais do projeto.

Este modulo le variaveis do arquivo `.env` e expoe um objeto `settings`
simples para o restante da aplicacao. A ideia e manter um unico ponto de
configuracao para caminho de armazenamento, banco e parametros basicos
de deteccao.
"""

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(slots=True)
class Settings:
    """Agrupa configuracoes usadas em toda a aplicacao.

    Os valores padrao foram escolhidos para permitir desenvolvimento local
    com o menor numero possivel de ajustes.
    """

    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/pigvision",
    )
    storage_dir: Path = Path(os.getenv("STORAGE_DIR", "data"))
    kinect_backend: str = os.getenv("KINECT_BACKEND", "auto")
    pixels_per_meter: float = float(os.getenv("PIXELS_PER_METER", "0") or "0")
    depth_scale_meter: float = float(os.getenv("DEPTH_SCALE_METER", "0.001"))
    min_contour_area: int = int(os.getenv("MIN_CONTOUR_AREA", "8000"))
    motion_threshold: int = int(os.getenv("MOTION_THRESHOLD", "25"))
    auto_start: bool = os.getenv("AUTO_START", "false").lower() == "true"


settings = Settings()
