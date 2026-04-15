# Guia de Testes

Este projeto ainda nao possui suite automatica de testes, mas voce consegue validar tudo manualmente de forma segura.

## 1. Teste de sintaxe

Verifica se os modulos Python compilam:

```bash
python3 -m compileall src
```

## 2. Teste de instalacao

Com ambiente virtual ativo:

```bash
pip install -e .
pigvision --help
```

Se o comando mostrar a lista de subcomandos, a instalacao basica esta correta.

## 3. Teste de banco

Garanta que o PostgreSQL esta no ar e rode:

```bash
pigvision init-db
```

Depois verifique se as tabelas existem:

```sql
\dt
```

Voce deve ver:
- `calibrations`
- `measurements`

## 4. Teste sem hardware

### Captura

```bash
pigvision capture-frame --backend mock
```

### Calibracao

```bash
pigvision calibrate \
  --image referencia.png \
  --point-a 100,200 \
  --point-b 500,200 \
  --distance-m 2.0 \
  --name teste-mock
```

### Medicao unica

```bash
pigvision measure-once --backend mock
```

### Monitoramento

```bash
pigvision monitor --backend mock --frames 50 --interval 0.2
```

## 5. Teste com hardware real

### Passo 1

Instale o backend correto:
- `freenect` para Kinect classico
- `pykinect2` para Kinect v2

### Passo 2

Teste captura:

```bash
pigvision capture-frame --backend freenect
```

Ou:

```bash
pigvision capture-frame --backend pykinect2
```

### Passo 3

Faça calibracao com regua real:

```bash
pigvision calibrate \
  --point-a 120,300 \
  --point-b 620,300 \
  --distance-m 2.0 \
  --name baia-real
```

### Passo 4

Execute medicao:

```bash
pigvision measure-once --backend freenect
```

## 6. Checklist de aceite

O projeto pode ser considerado funcional quando:

- instala sem erro
- cria banco sem erro
- captura frame no modo mock
- grava calibracao no banco
- salva preview de calibracao
- salva imagem anotada de medicao
- salva visualizacao de profundidade
- grava medicao no banco

## 7. Problemas comuns

### Erro de conexao com banco

Verifique:
- usuario
- senha
- host
- porta
- nome do banco

### `measure-once` retorna `no-object-detected`

Verifique:
- se existe calibracao salva
- se `PIXELS_PER_METER` esta configurado
- se o objeto tem area suficiente

### Sem profundidade

Pode acontecer quando:
- backend nao entregou frame de profundidade
- hardware nao esta pronto
- biblioteca nao esta instalada corretamente

## 8. Sugestao de proximo passo

Quando quiser, eu posso montar tambem:
- testes automatizados com `pytest`
- dados de exemplo
- script SQL para criar banco e usuario
- script shell para subir o ambiente mais rapido
