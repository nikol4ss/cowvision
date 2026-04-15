# Guia de Testes

Este documento consolida a estrategia de validacao do CowVision, cobrindo testes automatizados, testes manuais sem hardware e testes de integracao com Kinect real.

## Visao geral

O projeto hoje possui dois niveis principais de validacao:

- testes unitarios para a logica central
- testes manuais para validar ambiente, banco, CLI e fluxo operacional

A combinacao desses dois niveis permite validar a maior parte do sistema antes mesmo de conectar o Kinect.

## 1. Testes automatizados

A suite automatizada fica na pasta `tests/` e cobre os fluxos centrais do projeto.

Escopo atual:

- calibracao
- deteccao de movimento
- medicao com backend `mock`
- persistencia via servicos
- saida principal da CLI

Comando para executar localmente:

```bash
python -m unittest discover -s tests -v
```

Resultado esperado:

- todos os testes devem finalizar com status `OK`

## 2. Integracao continua

O repositorio possui workflow de CI em [.github/workflows/ci.yml](/Users/user/Workspaces/projects/cowvision/.github/workflows/ci.yml).

A pipeline executa:

- checkout do repositorio
- instalacao do projeto em modo editavel
- execucao da suite automatizada

A CI roda em:

- push para `main`
- push para branches `codex/**`
- pull requests

## 3. Validacoes locais recomendadas

Antes de abrir PR ou subir novas alteracoes, a rotina recomendada e:

1. compilar os modulos
2. rodar a suite automatizada
3. validar o fluxo manual sem hardware
4. revisar o banco e os arquivos gerados

Comandos uteis:

```bash
python3 -m compileall src
python -m unittest discover -s tests -v
```

## 4. Teste de instalacao

Com a virtualenv ativa:

```bash
pip install -e .
cowvision --help
```

Criterio de aceite:

- o comando `cowvision --help` deve listar os subcomandos disponiveis

## 5. Teste de banco

Garanta que o PostgreSQL esta em execucao e rode:

```bash
cowvision init-db
```

Depois, valide no `psql`:

```sql
\dt
```

Criterio de aceite:

- as tabelas `calibrations` e `measurements` devem existir

## 6. Teste sem hardware

O backend `mock` permite validar o fluxo operacional sem Kinect fisico.

### Captura

```bash
cowvision capture-frame --backend mock
```

### Calibracao

```bash
cowvision calibrate \
  --image referencia.png \
  --point-a 100,200 \
  --point-b 500,200 \
  --distance-m 2.0 \
  --name teste-mock
```

### Medicao unica

```bash
cowvision measure-once --backend mock
```

### Monitoramento

```bash
cowvision monitor --backend mock --frames 50 --interval 0.2
```

Criterios de aceite:

- o CLI deve responder sem erro
- imagens devem ser gravadas em `data/images/` e `data/depth/`
- registros devem aparecer no banco

## 7. Teste com hardware real

Quando o Kinect estiver disponivel, faca a validacao em etapas.

### Etapa 1: backend

Instale o backend correto:

- `freenect` para Kinect classico
- `pykinect2` para Kinect v2

### Etapa 2: captura

```bash
cowvision capture-frame --backend freenect
```

ou

```bash
cowvision capture-frame --backend pykinect2
```

### Etapa 3: calibracao real

```bash
cowvision calibrate \
  --point-a 120,300 \
  --point-b 620,300 \
  --distance-m 2.0 \
  --name baia-real
```

### Etapa 4: medicao

```bash
cowvision measure-once --backend freenect
```

## 8. Checklist de aceite

O sistema pode ser considerado funcional quando:

- a suite automatizada passa
- o projeto instala sem erro
- o banco inicializa com sucesso
- o backend `mock` retorna captura valida
- a calibracao e salva
- a medicao gera imagem anotada
- a profundidade e salva quando disponivel
- os dados aparecem no banco

## 9. Problemas comuns

### Erro de conexao com banco

Verifique:

- usuario
- senha
- host
- porta
- nome do banco
- se o PostgreSQL esta em execucao

### `measure-once` retorna `no-object-detected`

Verifique:

- se existe calibracao salva
- se `PIXELS_PER_METER` esta configurado
- se o objeto tem area suficiente
- se os limiares do ambiente estao adequados

### Sem profundidade

Pode ocorrer quando:

- o backend nao retornou frame de profundidade
- o hardware nao esta pronto
- a biblioteca do Kinect nao foi instalada corretamente

## 10. Evolucoes recomendadas

Como proximos passos de qualidade, as evolucoes mais naturais sao:

- adicionar cobertura para mais cenarios de CLI
- incluir dados de teste controlados
- criar validacao automatica de artefatos gerados
- medir cobertura de testes
- incluir testes de integracao opcionais com banco temporario
