# Arquitetura do CowVision

Este documento descreve a organizacao tecnica do projeto, suas camadas principais e o fluxo de dados desde a captura da cena ate a persistencia das medicoes.

## Objetivo arquitetural

CowVision foi estruturado para resolver um problema especifico com o minimo de complexidade acidental:

1. capturar imagem e profundidade
2. calibrar a relacao entre pixel e distancia real
3. detectar passagem de um objeto na cena
4. medir dimensoes principais da vaca
5. salvar evidencias visuais e dados estruturados

A arquitetura privilegia:

- separacao clara de responsabilidades
- operacao simples via CLI
- capacidade de teste sem hardware
- facil evolucao para cenarios reais de campo

## Fluxo principal

```text
Kinect / Mock
    -> FrameBundle
    -> MeasurementEngine
    -> MonitoringService
    -> FileStorage
    -> MeasurementRepository
    -> PostgreSQL
```

## Camadas do sistema

### 1. Configuracao

Arquivo: [src/cowvision/config.py](/Users/user/Workspaces/projects/cowvision/src/cowvision/config.py)

Responsavel por:

- carregar variaveis do `.env`
- expor configuracoes compartilhadas pela aplicacao
- centralizar parametros operacionais

Exemplos:

- `DATABASE_URL`
- `KINECT_BACKEND`
- `PIXELS_PER_METER`
- `MIN_CONTOUR_AREA`
- `MOTION_THRESHOLD`

### 2. Captura

Arquivo: [src/cowvision/kinect.py](/Users/user/Workspaces/projects/cowvision/src/cowvision/kinect.py)

Responsavel por:

- encapsular a origem dos frames
- manter uma interface unica para todos os backends
- permitir desenvolvimento sem sensor fisico

Implementacoes principais:

- `BaseKinectCamera`: contrato base
- `MockKinectCamera`: simulador para desenvolvimento e testes
- `FreenectCamera`: integracao com Kinect classico
- `PyKinect2Camera`: integracao com Kinect v2

### 3. Calibracao

Arquivo: [src/cowvision/calibration.py](/Users/user/Workspaces/projects/cowvision/src/cowvision/calibration.py)

Responsavel por:

- converter uma referencia conhecida em fator `pixels_per_meter`
- gerar uma imagem de preview para auditoria visual

Formula aplicada:

```text
pixels_per_meter = distancia_em_pixels / distancia_real_em_metros
```

Exemplo:

```text
2.0 metros = 500 pixels
pixels_per_meter = 500 / 2.0 = 250 px/m
```

### 4. Medicao

Arquivo: [src/cowvision/measurement.py](/Users/user/Workspaces/projects/cowvision/src/cowvision/measurement.py)

Responsavel por:

- detectar mudanca entre frames
- segmentar o maior objeto da cena
- medir dimensoes com base na calibracao
- estimar distancia usando profundidade

Pipeline atual:

1. conversao para escala de cinza
2. suavizacao com `GaussianBlur`
3. limiarizacao binaria
4. limpeza com operacoes morfologicas
5. extracao de contornos
6. selecao do maior contorno
7. medicao via `cv2.minAreaRect`

### 5. Orquestracao

Arquivo: [src/cowvision/services.py](/Users/user/Workspaces/projects/cowvision/src/cowvision/services.py)

Responsavel por:

- combinar os modulos tecnicos em fluxos completos
- salvar artefatos e registros sem expor detalhes ao CLI
- consolidar regras de uso de calibracao e persistencia

Servicos principais:

- `CalibrationService`
- `MonitoringService`

### 6. Persistencia

Arquivos:

- [src/cowvision/database.py](/Users/user/Workspaces/projects/cowvision/src/cowvision/database.py)
- [src/cowvision/models.py](/Users/user/Workspaces/projects/cowvision/src/cowvision/models.py)
- [src/cowvision/repositories.py](/Users/user/Workspaces/projects/cowvision/src/cowvision/repositories.py)
- [src/cowvision/storage.py](/Users/user/Workspaces/projects/cowvision/src/cowvision/storage.py)

Responsavel por:

- criar e gerenciar sessoes de banco
- mapear tabelas ORM
- registrar calibracoes e medicoes
- salvar imagens em disco com nomes unicos

## Entidades principais

### Calibracao

Representa a relacao entre distancia real e distancia em pixels para uma determinada configuracao de camera.

Dados principais:

- nome
- pixels por metro
- distancia real usada
- distancia em pixels
- observacoes
- data de criacao

### Medicao

Representa uma medicao automatica realizada pelo sistema.

Dados principais:

- dimensoes em pixels
- dimensoes em metros
- diametro estimado
- distancia do objeto
- confianca
- caminho da imagem anotada
- caminho da visualizacao de profundidade
- metadados complementares
- data de criacao

## Escolhas de design

Algumas decisoes foram intencionais:

- o backend `mock` existe para permitir desenvolvimento sem hardware
- a calibracao e linear para manter o projeto simples e operacional
- o maior contorno e usado como objeto principal para evitar heuristicas desnecessarias nesta fase
- a CLI e o ponto de entrada principal para facilitar operacao e testes

## Limitacoes atuais

O projeto ainda tem algumas simplificacoes importantes:

- calibracao linear simples, sem correcao geometrica avancada
- segmentacao baseada apenas no maior contorno
- ausencia de mascara de area de passagem
- ausencia de interface grafica
- ausencia de dataset real incorporado ao repositorio

Essas limitacoes sao coerentes com o objetivo atual do projeto: entregar uma base funcional, compreensivel e facil de evoluir.
