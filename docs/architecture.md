# Arquitetura do PigVision

## Objetivo

O projeto foi organizado para resolver um fluxo bem direto:

1. Capturar imagem e profundidade com Kinect.
2. Calibrar a relacao entre pixel e distancia real.
3. Detectar quando um objeto entra na cena.
4. Medir o objeto automaticamente.
5. Salvar imagem, profundidade e dados no PostgreSQL.

## Fluxo geral

```text
Kinect / Mock
    -> FrameBundle
    -> MeasurementEngine
    -> MonitoringService
    -> FileStorage
    -> MeasurementRepository
    -> PostgreSQL
```

## Camadas

### 1. Configuracao

Arquivo: [src/pigvision/config.py](/Users/user/Workspaces/projects/pigvision/src/pigvision/config.py)

Responsabilidade:
- ler `.env`
- expor configuracoes globais

Exemplos de configuracao:
- `DATABASE_URL`
- `KINECT_BACKEND`
- `PIXELS_PER_METER`
- `MIN_CONTOUR_AREA`

### 2. Captura

Arquivo: [src/pigvision/kinect.py](/Users/user/Workspaces/projects/pigvision/src/pigvision/kinect.py)

Responsabilidade:
- encapsular a origem dos frames
- manter a mesma interface para `freenect`, `pykinect2` e `mock`

Classes:
- `BaseKinectCamera`: contrato base
- `MockKinectCamera`: simulador
- `FreenectCamera`: Kinect classico
- `PyKinect2Camera`: Kinect v2

### 3. Calibracao

Arquivo: [src/pigvision/calibration.py](/Users/user/Workspaces/projects/pigvision/src/pigvision/calibration.py)

Responsabilidade:
- calcular `pixels_per_meter`

Formula:

```text
pixels_per_meter = distancia_em_pixels / distancia_real_em_metros
```

Exemplo:

```text
2.0 metros = 500 pixels
pixels_per_meter = 500 / 2.0 = 250 px/m
```

### 4. Medicao

Arquivo: [src/pigvision/measurement.py](/Users/user/Workspaces/projects/pigvision/src/pigvision/measurement.py)

Responsabilidade:
- detectar movimento
- segmentar o objeto principal
- medir largura e altura
- estimar distancia pela profundidade

Pipeline atual:
- converter para escala de cinza
- suavizar com `GaussianBlur`
- aplicar `threshold`
- limpar ruido com operacoes morfologicas
- extrair contornos
- escolher o maior contorno
- medir com `cv2.minAreaRect`

### 5. Orquestracao

Arquivo: [src/pigvision/services.py](/Users/user/Workspaces/projects/pigvision/src/pigvision/services.py)

Responsabilidade:
- combinar os modulos tecnicos em fluxos completos de negocio

Servicos:
- `CalibrationService`
- `MonitoringService`

### 6. Persistencia

Arquivos:
- [src/pigvision/database.py](/Users/user/Workspaces/projects/pigvision/src/pigvision/database.py)
- [src/pigvision/models.py](/Users/user/Workspaces/projects/pigvision/src/pigvision/models.py)
- [src/pigvision/repositories.py](/Users/user/Workspaces/projects/pigvision/src/pigvision/repositories.py)
- [src/pigvision/storage.py](/Users/user/Workspaces/projects/pigvision/src/pigvision/storage.py)

Responsabilidade:
- criar tabelas
- abrir sessoes
- gravar calibracoes e medicoes
- salvar imagens em disco

## Por que esta arquitetura e simples

- cada modulo tem uma responsabilidade pequena
- o fluxo principal cabe em poucos arquivos
- existe modo `mock`, entao da para desenvolver sem hardware
- o banco guarda apenas o essencial

## Limites atuais

- a calibracao usa apenas uma relacao linear simples
- o algoritmo mede o maior contorno da cena
- nao ha interface grafica
- nao ha testes automatizados ainda

Isso foi proposital para manter o projeto funcional e facil de entender.
