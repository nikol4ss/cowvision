# Tutorial Completo

Este tutorial mostra desde a instalacao ate o teste final do projeto.

## 1. Visao rapida

Voce vai:

1. criar ambiente Python
2. configurar PostgreSQL
3. instalar dependencias
4. criar o banco
5. testar com backend `mock`
6. calibrar o sistema
7. executar uma medicao
8. monitorar continuamente
9. depois trocar para o Kinect real

## 2. Requisitos

Antes de tudo, tenha:

- Python 3.10 ou superior
- PostgreSQL rodando
- `pip`
- opcionalmente um Kinect compativel

## 3. Preparar ambiente Python

No diretório do projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
```

Se quiser instalar suporte adicional ao Kinect:

```bash
pip install -e ".[kinect]"
```

Observacao:
- em Linux, o `freenect` costuma ser o caminho natural
- em Windows, o `pykinect2` e o caminho esperado

## 4. Configurar o `.env`

Copie o modelo:

```bash
cp .env.example .env
```

Exemplo de configuracao:

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

### O que cada variavel significa

`DATABASE_URL`
- endereco de conexao com PostgreSQL

`STORAGE_DIR`
- pasta raiz para salvar imagens

`KINECT_BACKEND`
- `mock`, `auto`, `freenect` ou `pykinect2`

`PIXELS_PER_METER`
- se maior que zero, usa esse valor fixo
- se igual a zero, usa a ultima calibracao salva no banco

`MIN_CONTOUR_AREA`
- area minima para considerar um objeto valido

`MOTION_THRESHOLD`
- sensibilidade da deteccao de movimento

## 5. Preparar PostgreSQL

Exemplo de criacao do banco:

```sql
CREATE DATABASE cowvision;
```

Exemplo de usuario, se precisar:

```sql
CREATE USER cowvision_user WITH PASSWORD 'cowvision_pass';
GRANT ALL PRIVILEGES ON DATABASE cowvision TO cowvision_user;
```

Se usar esse usuario, ajuste o `.env`:

```env
DATABASE_URL=postgresql+psycopg2://cowvision_user:cowvision_pass@localhost:5432/cowvision
```

## 6. Criar tabelas

Com ambiente ativo:

```bash
cowvision init-db
```

Saida esperada:

```text
Banco inicializado com sucesso.
```

## 7. Primeiro teste sem Kinect

Esse e o melhor caminho para validar que tudo esta instalado.

### Testar captura

```bash
cowvision capture-frame --backend mock
```

Saida esperada parecida com:

```json
{"color_shape": [480, 640, 3], "depth_shape": [480, 640]}
```

### Fazer uma calibracao simples

Como o modo `mock` gera um objeto artificial, voce pode calibrar com uma imagem externa ou com um frame capturado.

Se tiver uma imagem de referencia, use:

```bash
cowvision calibrate \
  --image referencia.png \
  --point-a 100,200 \
  --point-b 500,200 \
  --distance-m 2.0 \
  --name teste-inicial
```

Saida esperada:

```json
{"pixels_per_meter": 200.0, "reference_pixels": 400.0, "preview_path": "data/calibration/...png"}
```

Isso significa:
- 2 metros equivalem a 400 pixels
- portanto 1 metro equivale a 200 pixels

### Executar uma medicao unica

```bash
cowvision measure-once --backend mock
```

Se o objeto for detectado, a saida sera parecida com:

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

### Testar monitoramento

```bash
cowvision monitor --backend mock --frames 50 --interval 0.2
```

Saida esperada:

```json
{"measurements": 1}
```

Ou mais, dependendo do movimento detectado.

## 8. Verificar arquivos gerados

Depois dos testes, confira:

- `data/calibration/`
- `data/images/`
- `data/depth/`

Essas imagens ajudam muito a validar:
- se a calibracao esta correta
- se o contorno do objeto foi encontrado
- se a profundidade esta coerente

## 9. Verificar dados no banco

Voce pode usar SQL diretamente:

```sql
SELECT * FROM calibrations ORDER BY created_at DESC;
SELECT * FROM measurements ORDER BY created_at DESC;
```

O que esperar:

- em `calibrations`: um registro com pixels por metro
- em `measurements`: registros com dimensoes, confianca e caminhos das imagens

## 10. Migrar para o Kinect real

Quando o mock estiver funcionando:

1. conecte o Kinect
2. instale a biblioteca correta
3. ajuste `KINECT_BACKEND`
4. teste captura
5. refaca a calibracao com o equipamento fixo

### Exemplo

No `.env`:

```env
KINECT_BACKEND=freenect
```

Ou:

```env
KINECT_BACKEND=pykinect2
```

Depois:

```bash
cowvision capture-frame --backend freenect
```

Se tudo estiver certo, refaça a calibracao real:

```bash
cowvision calibrate \
  --point-a 120,300 \
  --point-b 620,300 \
  --distance-m 2.0 \
  --name baia-01
```

## 11. Fluxo operacional recomendado em campo

1. Fixe o Kinect sempre na mesma altura e angulo.
2. Delimite a area por onde a vaca deve passar.
3. Coloque uma regua ou referencia conhecida na cena.
4. Execute a calibracao.
5. Confira a imagem gerada.
6. Rode o monitoramento.
7. Revise as primeiras medicoes e ajuste os limiares se necessario.

## 12. Como interpretar os resultados

### `width_m`

Maior dimensao do retangulo ajustado ao objeto.

### `height_m`

Menor dimensao do retangulo ajustado ao objeto.

### `diameter_m`

Media simples entre as duas dimensoes principais.

### `distance_m`

Mediana dos valores de profundidade dentro do contorno segmentado.

### `confidence`

Indicador simples proporcional ao tamanho do objeto na imagem.
Nao e uma probabilidade estatistica rigorosa.

## 13. Ajustes finos mais comuns

Se o sistema nao detectar a vaca:
- reduza `MIN_CONTOUR_AREA`
- reduza `MOTION_THRESHOLD`

Se estiver detectando ruido:
- aumente `MIN_CONTOUR_AREA`
- aumente `MOTION_THRESHOLD`
- melhore iluminacao e fundo

Se a medida em metros estiver errada:
- refaça a calibracao
- garanta que a referencia esta no mesmo plano da vaca
- mantenha o Kinect fixo

## 14. Ordem recomendada de validacao

1. `capture-frame --backend mock`
2. `calibrate`
3. `measure-once --backend mock`
4. `monitor --backend mock`
5. trocar para Kinect real
6. calibrar novamente
7. validar no ambiente real

## 15. O que ainda pode evoluir

Depois que a base estiver funcionando, os proximos passos naturais sao:

- adicionar testes automatizados
- criar mascara da area de passagem
- melhorar segmentacao usando profundidade
- gerar relatorios
- criar API ou interface web
