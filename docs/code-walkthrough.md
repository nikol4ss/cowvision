# Codigo Explicado

Este documento explica cada parte importante do projeto em linguagem direta.

## `src/pigvision/cli.py`

Papel:
- receber comandos do terminal
- chamar os servicos corretos

Comandos:
- `init-db`: cria as tabelas
- `capture-frame`: testa captura
- `calibrate`: grava calibracao
- `measure-once`: mede uma vez
- `monitor`: roda loop de monitoramento

### Como a calibracao entra no sistema

No comando `calibrate`, voce informa:
- imagem ou camera
- ponto A
- ponto B
- distancia real entre os pontos

O CLI manda isso para `CalibrationService`, que:
- calcula `pixels_per_meter`
- salva a imagem anotada
- grava no banco

## `src/pigvision/kinect.py`

Esse arquivo serve para padronizar a captura.

Mesmo que a origem seja diferente, o retorno e sempre um `FrameBundle` com:
- `color`
- `depth`
- `timestamp`

### Modo `mock`

Foi criado para voce poder testar:
- instalacao
- pipeline
- banco
- salvamento de imagens

Sem depender de Kinect fisico.

## `src/pigvision/measurement.py`

Este e o coracao da medicao.

### `detect_motion`

Compara dois frames:
- converte ambos para cinza
- calcula diferenca absoluta
- aplica limiar
- conta pixels alterados

Se muitos pixels mudaram, consideramos que algo passou.

### `measure`

Executa a segmentacao do objeto:

1. copia o frame colorido
2. converte para cinza
3. aplica blur
4. aplica threshold
5. limpa ruidos
6. encontra contornos
7. pega o maior contorno
8. mede com `minAreaRect`

### Por que usar `minAreaRect`

Porque ele mede uma caixa rotacionada, nao apenas horizontal.
Isso ajuda quando o animal nao esta perfeitamente alinhado com a imagem.

### Como a medida em metros e obtida

Depois da calibracao, temos:

```text
pixels_per_meter = X
```

Entao:

```text
largura_m = largura_px / pixels_per_meter
altura_m = altura_px / pixels_per_meter
```

## `src/pigvision/services.py`

Esse arquivo amarra o fluxo completo.

### `CalibrationService`

Responsavel por:
- chamar o calibrador
- salvar preview
- inserir calibracao no banco

### `MonitoringService`

Responsavel por:
- capturar frames
- detectar movimento
- medir
- salvar imagem
- salvar profundidade
- inserir no banco

## `src/pigvision/models.py`

Existem duas tabelas:

### `calibrations`

Guarda:
- nome
- pixels por metro
- distancia real usada
- distancia em pixels
- observacoes

### `measurements`

Guarda:
- largura e altura em pixels
- largura, altura e diametro em metros
- distancia do objeto
- confianca
- caminhos das imagens
- metadados em JSON

## `src/pigvision/storage.py`

Tem apenas uma responsabilidade:
- salvar arquivos em disco com nome unico

Pastas geradas:
- `data/images`
- `data/depth`
- `data/calibration`

## `src/pigvision/database.py`

Centraliza:
- engine do SQLAlchemy
- sessao
- transacao com commit/rollback

O `session_scope()` existe para evitar repeticao e deixar o codigo mais seguro.

## Como estudar o projeto

Uma boa ordem para leitura e:

1. [src/pigvision/cli.py](/Users/user/Workspaces/projects/pigvision/src/pigvision/cli.py)
2. [src/pigvision/services.py](/Users/user/Workspaces/projects/pigvision/src/pigvision/services.py)
3. [src/pigvision/measurement.py](/Users/user/Workspaces/projects/pigvision/src/pigvision/measurement.py)
4. [src/pigvision/kinect.py](/Users/user/Workspaces/projects/pigvision/src/pigvision/kinect.py)
5. [src/pigvision/models.py](/Users/user/Workspaces/projects/pigvision/src/pigvision/models.py)
6. [src/pigvision/storage.py](/Users/user/Workspaces/projects/pigvision/src/pigvision/storage.py)
