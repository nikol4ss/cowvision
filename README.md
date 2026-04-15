# CowVision

Estrutura simples e funcional para medir vacas com Kinect, calibrar relacao pixel x distancia real e registrar imagens e dados no PostgreSQL.

Se voce quer um guia completo de estudo e operacao, leia tambem:

- [Visao Geral da Arquitetura](/Users/user/Workspaces/projects/pigvision/docs/architecture.md)
- [Tutorial Completo de Instalacao e Uso](/Users/user/Workspaces/projects/pigvision/docs/tutorial.md)
- [Guia de Testes](/Users/user/Workspaces/projects/pigvision/docs/testing.md)

## O que o projeto faz

- Captura imagem colorida e profundidade com Kinect usando `freenect` ou `pykinect2`
- Permite calibracao com uma regua ou referencia conhecida
- Detecta passagem de objeto com comparacao entre frames
- Mede largura e diametro em pixels e metros
- Salva imagem anotada, mapa de profundidade e dados no PostgreSQL

## Estrutura

```text
src/cowvision/
  cli.py            # Comandos principais
  config.py         # Variaveis de ambiente
  database.py       # SQLAlchemy e sessao
  models.py         # Tabelas de calibracao e medicao
  kinect.py         # Integracao Kinect e modo mock
  calibration.py    # Relacao pixel x metro
  measurement.py    # Deteccao e medicao
  services.py       # Fluxos de calibracao e monitoramento
  storage.py        # Salvamento de imagens
```

Documentacao detalhada arquivo por arquivo:

- [Codigo Explicado](/Users/user/Workspaces/projects/pigvision/docs/code-walkthrough.md)

## Requisitos

- Python 3.10+
- PostgreSQL
- Kinect compativel com `freenect` ou `pykinect2`

## Instalacao

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
```

Se for usar Kinect no Linux:

```bash
pip install -e ".[kinect]"
```

## Configuracao

Ajuste o arquivo `.env`:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/cowvision
STORAGE_DIR=data
KINECT_BACKEND=auto
PIXELS_PER_METER=0
MIN_CONTOUR_AREA=8000
MOTION_THRESHOLD=25
```

`PIXELS_PER_METER` pode ficar `0` quando voce quiser usar a ultima calibracao salva no banco.

## Uso

Inicializar tabelas:

```bash
cowvision init-db
```

Capturar um frame para testar a camera:

```bash
cowvision capture-frame --backend mock
```

Calibrar usando uma imagem existente:

```bash
cowvision calibrate \
  --image referencia.png \
  --point-a 120,300 \
  --point-b 620,300 \
  --distance-m 2.0 \
  --name regua-baia-01
```

Medir uma unica passagem:

```bash
cowvision measure-once --backend mock
```

Monitorar continuamente:

```bash
cowvision monitor --backend mock --frames 200 --interval 0.3
```

## Documentacao recomendada

- [Tutorial Completo](/Users/user/Workspaces/projects/pigvision/docs/tutorial.md)
- [Como Testar Sem Kinect](/Users/user/Workspaces/projects/pigvision/docs/testing.md)
- [Entendendo o Codigo](/Users/user/Workspaces/projects/pigvision/docs/code-walkthrough.md)

## Fluxo recomendado no hardware real

1. Fixar o Kinect na mesma posicao de trabalho.
2. Posicionar uma regua ou referencia conhecida no campo de visao.
3. Executar a calibracao e validar a imagem gerada em `data/calibration/`.
4. Rodar `cowvision monitor`.
5. Conferir as imagens anotadas em `data/images/` e os registros no PostgreSQL.

## Observacoes praticas

- O modo `mock` permite desenvolver sem o Kinect conectado.
- O algoritmo atual privilegia simplicidade: segmenta o maior contorno do frame.
- Para ambiente real, o proximo passo natural e adicionar mascara da area de passagem e filtros especificos do cenario.
