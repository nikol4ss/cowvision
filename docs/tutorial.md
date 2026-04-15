# Tutorial Completo

Este tutorial apresenta o fluxo completo de instalacao, configuracao, operacao e validacao do CowVision. A proposta e permitir que voce coloque o projeto para funcionar primeiro em modo `mock` e depois avance para o Kinect real com seguranca.

## Objetivo do tutorial

Ao final deste guia, voce tera conseguido:

- instalar o projeto em ambiente Python isolado
- configurar o PostgreSQL
- criar o banco e as tabelas
- validar o pipeline sem Kinect fisico
- executar calibracao, medicao unica e monitoramento
- entender como migrar para o hardware real

## 1. Requisitos

Antes de iniciar, tenha disponivel:

- Python 3.10 ou superior
- `pip`
- PostgreSQL instalado e em execucao
- opcionalmente, Kinect compativel com `freenect` ou `pykinect2`

## 2. Preparar o ambiente Python

No diretorio do projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
```

Se voce pretende usar Kinect depois:

```bash
pip install -e ".[kinect]"
```

Observacoes:

- em Linux, `freenect` costuma ser o caminho mais natural
- em Windows, `pykinect2` tende a ser a opcao mais direta
- para validacao inicial, o backend `mock` e suficiente

## 3. Configurar variaveis de ambiente

Crie o arquivo `.env` a partir do modelo:

```bash
cp .env.example .env
```

Exemplo de configuracao recomendada para desenvolvimento local:

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

Significado dos campos principais:

- `DATABASE_URL`: string de conexao com o PostgreSQL
- `STORAGE_DIR`: pasta onde imagens e artefatos serao salvos
- `KINECT_BACKEND`: backend ativo do sensor
- `PIXELS_PER_METER`: fator fixo de calibracao; se `0`, usa o ultimo salvo no banco
- `MIN_CONTOUR_AREA`: area minima para aceitar um objeto como valido
- `MOTION_THRESHOLD`: limiar de sensibilidade da deteccao de movimento

## 4. Preparar o PostgreSQL

Se o PostgreSQL ja estiver em execucao, entre no `psql`:

```bash
psql postgres
```

Crie o banco:

```sql
CREATE DATABASE cowvision;
```

Opcionalmente, crie um usuario dedicado:

```sql
CREATE USER cowvision_user WITH PASSWORD 'cowvision_pass';
GRANT ALL PRIVILEGES ON DATABASE cowvision TO cowvision_user;
```

Se optar por esse usuario, ajuste o `.env`:

```env
DATABASE_URL=postgresql+psycopg2://cowvision_user:cowvision_pass@localhost:5432/cowvision
```

Saia do `psql` com:

```sql
\q
```

## 5. Criar as tabelas

Com a virtualenv ativa e o `.env` configurado:

```bash
cowvision init-db
```

Saida esperada:

```text
Banco inicializado com sucesso.
```

Se quiser validar no banco:

```bash
psql cowvision
```

E no prompt do PostgreSQL:

```sql
\dt
```

Voce deve ver as tabelas `calibrations` e `measurements`.

## 6. Validar o sistema sem Kinect fisico

Esta e a etapa mais importante para confirmar que a base do projeto esta correta antes de conectar hardware.

### 6.1 Testar captura simulada

```bash
cowvision capture-frame --backend mock
```

Saida esperada aproximada:

```json
{"color_shape": [480, 640, 3], "depth_shape": [480, 640]}
```

Isso confirma que o backend `mock` esta gerando frame colorido e profundidade artificial.

### 6.2 Definir uma estrategia de calibracao

Voce tem duas opcoes nesta fase.

Opcao A: calibrar com uma imagem de referencia

```bash
cowvision calibrate \
  --image referencia.png \
  --point-a 100,200 \
  --point-b 500,200 \
  --distance-m 2.0 \
  --name teste-inicial
```

Saida esperada aproximada:

```json
{"pixels_per_meter": 200.0, "reference_pixels": 400.0, "preview_path": "data/calibration/...png"}
```

Opcao B: definir um valor fixo no `.env` para testes rapidos

```env
PIXELS_PER_METER=200
```

A opcao B e util quando voce quer apenas validar o fluxo completo sem depender de uma imagem de referencia nesse momento.

### 6.3 Executar uma medicao unica

```bash
cowvision measure-once --backend mock
```

Saida esperada aproximada:

```json
{
  "width_m": 0.88,
  "height_m": 0.56,
  "diameter_m": 0.72,
  "distance_m": 0.85,
  "image_path": "data/images/measurement_....png",
  "depth_path": "data/depth/depth_....png"
}
```

### 6.4 Executar monitoramento continuo

```bash
cowvision monitor --backend mock --frames 50 --interval 0.2
```

Saida esperada:

```json
{"measurements": 1}
```

O numero pode variar conforme o movimento detectado entre os frames sinteticos.

## 7. Validar artefatos gerados

Depois dos testes, confira:

- `data/calibration/`
- `data/images/`
- `data/depth/`

O que observar:

- se a imagem de calibracao foi salva corretamente
- se a caixa de medicao foi desenhada sobre o objeto
- se a profundidade foi gerada e salva
- se os nomes dos arquivos estao coerentes

## 8. Validar registros no banco

Entre no banco:

```bash
psql cowvision
```

Consultas uteis:

```sql
SELECT * FROM calibrations ORDER BY created_at DESC;
SELECT * FROM measurements ORDER BY created_at DESC;
```

O que esperar:

- em `calibrations`: fator de conversao pixels/metro
- em `measurements`: dimensoes, confianca, distancia e caminhos dos arquivos

## 9. Migrar para o Kinect real

Quando o fluxo `mock` estiver validado, troque para o hardware real.

Passos recomendados:

1. conecte o Kinect
2. instale a biblioteca adequada
3. ajuste `KINECT_BACKEND`
4. valide captura
5. refaca a calibracao com o sensor na posicao definitiva
6. execute medicao e monitoramento de campo

Exemplo de configuracao:

```env
KINECT_BACKEND=freenect
```

ou

```env
KINECT_BACKEND=pykinect2
```

Teste inicial:

```bash
cowvision capture-frame --backend freenect
```

Depois refaça a calibracao real:

```bash
cowvision calibrate \
  --point-a 120,300 \
  --point-b 620,300 \
  --distance-m 2.0 \
  --name baia-real
```

## 10. Boas praticas de operacao em campo

Para obter medidas mais consistentes:

- fixe o Kinect sempre na mesma altura e angulo
- controle a area por onde a vaca deve passar
- mantenha a referencia de calibracao no mesmo plano de interesse
- revise as primeiras medicoes antes de confiar no fluxo automatico
- ajuste `MIN_CONTOUR_AREA` e `MOTION_THRESHOLD` conforme o ambiente real

## 11. Interpretacao dos resultados

- `width_m`: maior dimensao da caixa rotacionada detectada
- `height_m`: menor dimensao da caixa rotacionada detectada
- `diameter_m`: media simples entre as duas dimensoes principais
- `distance_m`: estimativa de distancia baseada na mediana da profundidade do contorno
- `confidence`: indicador simples baseado na area relativa do objeto no frame

## 12. Solucao de problemas comuns

Se `init-db` falhar:

- confirme se o PostgreSQL esta rodando
- confirme usuario, senha, host, porta e nome do banco no `.env`

Se `measure-once` retornar `no-object-detected`:

- confira se existe calibracao salva ou se `PIXELS_PER_METER` esta definido
- reduza `MIN_CONTOUR_AREA`
- revise o frame e a iluminacao

Se as medidas em metros estiverem incoerentes:

- refaça a calibracao
- garanta que a referencia esteja no plano correto
- mantenha o sensor fixo entre calibracao e medicao

## 13. Ordem recomendada de validacao

1. instalar projeto
2. configurar banco e `.env`
3. rodar `init-db`
4. validar `capture-frame --backend mock`
5. calibrar ou definir `PIXELS_PER_METER`
6. rodar `measure-once --backend mock`
7. rodar `monitor --backend mock`
8. validar imagens e banco
9. migrar para Kinect real
