from __future__ import annotations

"""Interface de linha de comando do PigVision.

Comandos principais:
- `init-db`: cria as tabelas
- `capture-frame`: valida captura do backend
- `calibrate`: salva uma calibracao a partir de dois pontos
- `measure-once`: mede um unico frame
- `monitor`: monitora continuamente e registra medicoes
"""

import argparse
import json
from pathlib import Path

import cv2

from pigvision.config import settings
from pigvision.database import Base, engine
from pigvision.kinect import build_camera
from pigvision.services import CalibrationService, MonitoringService


def build_parser() -> argparse.ArgumentParser:
    """Constroi o parser principal e seus subcomandos."""

    parser = argparse.ArgumentParser(description="PigVision: medicao de suinos com Kinect")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init-db", help="Cria as tabelas no PostgreSQL")

    capture_parser = subparsers.add_parser("capture-frame", help="Captura um frame colorido e imprime suas dimensoes")
    capture_parser.add_argument("--backend", default=settings.kinect_backend)

    calibrate_parser = subparsers.add_parser("calibrate", help="Executa calibracao usando dois pontos da imagem")
    calibrate_parser.add_argument("--image", help="Caminho da imagem. Se omitido, captura da camera.")
    calibrate_parser.add_argument("--point-a", required=True, help="Ponto inicial no formato x,y")
    calibrate_parser.add_argument("--point-b", required=True, help="Ponto final no formato x,y")
    calibrate_parser.add_argument("--distance-m", required=True, type=float, help="Distancia real em metros")
    calibrate_parser.add_argument("--name", default="default")
    calibrate_parser.add_argument("--notes", default=None)
    calibrate_parser.add_argument("--backend", default=settings.kinect_backend)

    measure_parser = subparsers.add_parser("measure-once", help="Captura e mede um unico objeto")
    measure_parser.add_argument("--backend", default=settings.kinect_backend)

    monitor_parser = subparsers.add_parser("monitor", help="Monitora a passagem de objetos e mede automaticamente")
    monitor_parser.add_argument("--backend", default=settings.kinect_backend)
    monitor_parser.add_argument("--frames", type=int, default=100)
    monitor_parser.add_argument("--interval", type=float, default=0.3)
    return parser


def parse_point(value: str) -> tuple[int, int]:
    """Converte `x,y` em uma tupla de inteiros."""

    x_str, y_str = value.split(",", maxsplit=1)
    return int(x_str), int(y_str)


def command_init_db() -> None:
    """Cria as tabelas definidas pelos modelos ORM."""

    Base.metadata.create_all(bind=engine)
    print("Banco inicializado com sucesso.")


def command_capture_frame(backend: str) -> None:
    """Captura um frame e imprime o tamanho dos arrays retornados."""

    camera = build_camera(backend)
    frame = camera.get_frame()
    print(
        json.dumps(
            {
                "color_shape": list(frame.color.shape),
                "depth_shape": list(frame.depth.shape) if frame.depth is not None else None,
            },
            ensure_ascii=True,
        )
    )


def command_calibrate(args: argparse.Namespace) -> None:
    """Executa a calibracao a partir de uma imagem ou da camera."""

    if args.image:
        image = cv2.imread(str(Path(args.image)))
        if image is None:
            raise FileNotFoundError(f"Imagem nao encontrada: {args.image}")
    else:
        image = build_camera(args.backend).get_frame().color

    result, preview_path = CalibrationService().calibrate(
        image=image,
        point_a=parse_point(args.point_a),
        point_b=parse_point(args.point_b),
        reference_distance_m=args.distance_m,
        name=args.name,
        notes=args.notes,
    )
    print(
        json.dumps(
            {
                "pixels_per_meter": result.pixels_per_meter,
                "reference_pixels": result.reference_pixels,
                "preview_path": str(preview_path),
            },
            ensure_ascii=True,
        )
    )


def command_measure_once(backend: str) -> None:
    """Captura e registra uma unica medicao, se houver objeto valido."""

    service = MonitoringService(camera=build_camera(backend))
    result = service.capture_once()
    if result is None:
        print(json.dumps({"status": "no-object-detected"}, ensure_ascii=True))
        return
    print(
        json.dumps(
            {
                "width_m": result.width_m,
                "height_m": result.height_m,
                "diameter_m": result.diameter_m,
                "distance_m": result.distance_m,
                "image_path": str(result.image_path),
                "depth_path": str(result.depth_path) if result.depth_path else None,
            },
            ensure_ascii=True,
        )
    )


def command_monitor(backend: str, frames: int, interval: float) -> None:
    """Executa um loop simples de monitoramento automatico."""

    service = MonitoringService(camera=build_camera(backend))
    results = service.monitor(interval_seconds=interval, max_frames=frames)
    print(json.dumps({"measurements": len(results)}, ensure_ascii=True))


def main() -> None:
    """Ponto de entrada do executavel `pigvision`."""

    parser = build_parser()
    args = parser.parse_args()

    if args.command == "init-db":
        command_init_db()
    elif args.command == "capture-frame":
        command_capture_frame(args.backend)
    elif args.command == "calibrate":
        command_calibrate(args)
    elif args.command == "measure-once":
        command_measure_once(args.backend)
    elif args.command == "monitor":
        command_monitor(args.backend, args.frames, args.interval)


if __name__ == "__main__":
    main()
