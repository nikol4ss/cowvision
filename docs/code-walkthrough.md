# Walkthrough do Codigo

Este documento apresenta uma leitura guiada do codigo-fonte para quem quer entender como o CowVision funciona internamente.

## Ordem recomendada de leitura

Se voce estiver conhecendo o projeto agora, a ordem abaixo costuma ser a mais eficiente:

1. [src/cowvision/cli.py](/Users/user/Workspaces/projects/cowvision/src/cowvision/cli.py)
2. [src/cowvision/services.py](/Users/user/Workspaces/projects/cowvision/src/cowvision/services.py)
3. [src/cowvision/measurement.py](/Users/user/Workspaces/projects/cowvision/src/cowvision/measurement.py)
4. [src/cowvision/kinect.py](/Users/user/Workspaces/projects/cowvision/src/cowvision/kinect.py)
5. [src/cowvision/models.py](/Users/user/Workspaces/projects/cowvision/src/cowvision/models.py)
6. [src/cowvision/storage.py](/Users/user/Workspaces/projects/cowvision/src/cowvision/storage.py)

## `src/cowvision/cli.py`

Este arquivo e a porta de entrada operacional do sistema.

Responsabilidades:

- receber comandos via terminal
- interpretar argumentos
- acionar os servicos corretos
- imprimir respostas simples em formato facil de consumir

Comandos principais:

- `init-db`: cria as tabelas do banco
- `capture-frame`: valida a captura do backend
- `calibrate`: executa e grava uma calibracao
- `measure-once`: mede um unico frame
- `monitor`: executa monitoramento continuo

Ponto importante:

O CLI nao concentra regra de negocio. Ele apenas coleta parametros, chama servicos e apresenta o resultado. Isso ajuda a manter o projeto modular.

## `src/cowvision/services.py`

Esse modulo concentra os fluxos de alto nivel.

### `CalibrationService`

Responsavel por:

- chamar o calibrador
- salvar a imagem de preview
- registrar a calibracao no banco
- recuperar o fator de calibracao atual quando necessario

### `MonitoringService`

Responsavel por:

- capturar frames da camera
- detectar movimento entre frames
- disparar a medicao quando houver atividade
- persistir imagens e resultados no banco

Este modulo e onde a aplicacao fica mais proxima do fluxo real de operacao.

## `src/cowvision/measurement.py`

Este e o coracao da logica de visao computacional.

### `detect_motion`

Compara dois frames consecutivos para decidir se algo mudou na cena.

Passos:

1. converte os dois frames para cinza
2. calcula a diferenca absoluta
3. aplica limiarizacao
4. conta quantos pixels mudaram

Se a quantidade de pixels alterados passar do limite, o sistema considera que houve movimento suficiente para tentar medir.

### `measure`

Executa a segmentacao e medicao do objeto principal do frame.

Pipeline:

1. copia a imagem original
2. converte para tons de cinza
3. aplica suavizacao com `GaussianBlur`
4. gera uma mascara binaria com `threshold`
5. limpa ruidos com operacoes morfologicas
6. extrai os contornos externos
7. escolhe o maior contorno
8. mede com `minAreaRect`
9. estima a distancia usando profundidade
10. gera uma imagem anotada com as informacoes da medicao

### Por que usar `minAreaRect`

`minAreaRect` calcula a menor caixa rotacionada que envolve o contorno. Isso e melhor que medir apenas uma caixa horizontal quando a vaca aparece inclinada no frame.

### Conversao de pixels para metros

A conversao depende diretamente da calibracao:

```text
pixels_per_meter = X
largura_m = largura_px / X
altura_m = altura_px / X
```

## `src/cowvision/kinect.py`

Esse modulo padroniza a origem dos frames.

Independentemente do backend, a saida final e um `FrameBundle` com:

- `color`
- `depth`
- `timestamp`

### `MockKinectCamera`

Foi criada para permitir:

- desenvolvimento local
- validacao da pipeline
- execucao de testes automatizados
- uso do projeto sem depender de hardware

Ela gera uma elipse sintetica que se desloca no frame, simulando um objeto em movimento.

## `src/cowvision/models.py`

Define as duas entidades principais persistidas no banco.

### `CalibrationRecord`

Armazena:

- nome da calibracao
- pixels por metro
- distancia real usada
- distancia em pixels
- observacoes
- data de criacao

### `MeasurementRecord`

Armazena:

- dimensoes em pixels
- dimensoes em metros
- diametro estimado
- distancia do objeto
- confianca
- caminhos dos arquivos gerados
- metadados em JSON
- data de criacao

## `src/cowvision/storage.py`

Cuida da persistencia em disco dos artefatos visuais.

Diretorios gerados:

- `data/images/`: imagens anotadas das medicoes
- `data/depth/`: mapas de profundidade convertidos para visualizacao
- `data/calibration/`: previews das calibracoes

A ideia aqui e simples: deixar a persistencia de arquivos desacoplada da logica de medicao.

## `src/cowvision/database.py`

Centraliza a infraestrutura de banco.

Responsabilidades:

- criar o engine do SQLAlchemy
- fornecer sessoes
- padronizar commit e rollback com `session_scope()`

Esse desenho evita repeticao e reduz o risco de deixar transacoes abertas.

## `src/cowvision/repositories.py`

Implementa uma camada leve de acesso aos dados.

Papel:

- encapsular insercoes e consultas mais comuns
- reduzir acoplamento direto entre servicos e modelos ORM

Mesmo sendo simples, essa camada ajuda a manter os servicos mais legiveis.

## Conclusao

O CowVision foi estruturado para ser facil de entender e facil de evoluir. A maior parte da logica importante esta concentrada em poucos modulos, com fronteiras bem definidas entre CLI, servicos, visao computacional, persistencia e acesso ao hardware.
