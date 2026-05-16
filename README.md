# CowVision

CowVision e uma base em Python para captacao, calibracao e medicao automatica de vacas usando Kinect. O projeto transforma informacoes de imagem e profundidade em medidas reais, registra as evidencias visuais da medicao e persiste os dados em PostgreSQL.

## Visao geral

O sistema foi desenhado para um fluxo simples e objetivo:

- capturar imagem colorida e profundidade com Kinect
- calibrar a relacao entre pixel e distancia real
- detectar automaticamente a passagem de um objeto pela cena
- medir dimensoes principais da vaca no frame
- salvar imagens anotadas, visualizacao de profundidade e registros no banco

A implementacao prioriza simplicidade operacional. Por isso, o projeto ja inclui um backend `mock`, que permite desenvolver, testar e validar o fluxo sem Kinect fisico.

## Principais capacidades

- suporte a `freenect` e `pykinect2`
- backend `mock` para desenvolvimento sem hardware
- calibracao baseada em referencia conhecida
- deteccao simples de movimento entre frames
- medicao em pixels e metros
- persistencia de calibracoes e medicoes em PostgreSQL
- salvamento de imagens anotadas e mapas de profundidade
- CLI para operacao, testes e diagnostico
- testes unitarios e CI com GitHub Actions

## Estrutura do projeto

```text
src/cowvision/
  cli.py            Interface de linha de comando
  config.py         Configuracoes do projeto via .env
  database.py       Engine, sessao e transacao do SQLAlchemy
  models.py         Modelos ORM de calibracao e medicao
  kinect.py         Integracao com Kinect e backend mock
  calibration.py    Calculo da relacao pixel x metro
  measurement.py    Deteccao e medicao do objeto no frame
  services.py       Orquestracao dos fluxos principais
  storage.py        Persistencia de imagens em disco
```

## Requisitos

- Python 3.10 ou superior
- PostgreSQL
- opcionalmente, Kinect compativel com `freenect` ou `pykinect2`

## Instalacao rapida

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
cp .env.example .env
```

Para instalar suporte adicional ao Kinect:

```bash
pip install -e ".[kinect]"
```

## Configuracao

Exemplo de `.env`:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/cowvision
STORAGE_DIR=data
KINECT_BACKEND=mock
PIXELS_PER_METER=0
DEPTH_SCALE_METER=0.001
MIN_CONTOUR_AREA=8000
MOTION_THRESHOLD=25
AUTO_START=false
```

Valores mais importantes:

- `DATABASE_URL`: string de conexao com o PostgreSQL
- `KINECT_BACKEND`: `mock`, `auto`, `freenect` ou `pykinect2`
- `PIXELS_PER_METER`: se maior que zero, usa valor fixo; se zero, usa a ultima calibracao salva
- `MIN_CONTOUR_AREA`: area minima para considerar um objeto valido
- `MOTION_THRESHOLD`: sensibilidade da deteccao de movimento

## Uso basico

Inicializar o banco:

```bash
cowvision init-db
```

Testar captura sem hardware:

```bash
cowvision capture-frame --backend mock
```

Calibrar usando uma imagem:

```bash
cowvision calibrate \
  --image referencia.png \
  --point-a 120,300 \
  --point-b 620,300 \
  --distance-m 2.0 \
  --name baia-01
```

Executar uma medicao unica:

```bash
cowvision measure-once --backend mock
```

Monitorar continuamente:

```bash
cowvision monitor --backend mock --frames 200 --interval 0.3
```

## Fluxo recomendado de validacao

Sem Kinect fisico:

1. instalar o projeto
2. criar o banco PostgreSQL
3. rodar `cowvision init-db`
4. validar `cowvision capture-frame --backend mock`
5. calibrar com imagem de referencia ou definir `PIXELS_PER_METER`
6. testar `measure-once`
7. testar `monitor`
8. verificar imagens geradas e registros no banco

Com Kinect fisico:

1. fixar o sensor na posicao definitiva
2. instalar o backend correto
3. validar captura
4. refazer a calibracao com referencia real
5. executar monitoramento de campo
6. revisar as primeiras medicoes e ajustar limiares se necessario

## Testes

Rodar a suite automatizada:

```bash
python -m unittest discover -s tests -v
```

O projeto tambem possui CI em GitHub Actions para validar a suite em push e pull request.

## Documentacao complementar

- [Tutorial Completo](/Users/user/Workspaces/projects/cowvision/docs/tutorial.md)
- [Guia de Arquitetura](/Users/user/Workspaces/projects/cowvision/docs/architecture.md)
- [Guia de Testes](/Users/user/Workspaces/projects/cowvision/docs/testing.md)
- [Walkthrough do Codigo](/Users/user/Workspaces/projects/cowvision/docs/code-walkthrough.md)

## Estado atual e proximos passos

O projeto esta funcional para desenvolvimento, testes sem hardware e integracao inicial com Kinect. Como evolucoes naturais, os proximos passos mais provaveis sao:

- melhorar a segmentacao com filtros por profundidade
- delimitar a area de passagem da vaca
- adicionar relatorios ou API
- criar dataset de validacao real
- medir desempenho em ambiente de campo
