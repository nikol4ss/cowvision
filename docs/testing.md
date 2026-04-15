# Guia de Testes

Este projeto possui dois niveis de validacao:

- testes automatizados para a logica central
- testes manuais para validar banco, fluxo CLI e operacao sem hardware

## 1. Testes automatizados

Os testes unitarios ficam na pasta tests/ e cobrem:

- calibracao
- deteccao e medicao
- servicos de monitoramento
- saida principal da CLI

Para rodar localmente, execute:
python -m unittest discover -s tests -v

## 2. Integracao continua

O projeto tambem possui pipeline em .github/workflows/ci.yml.

Essa CI executa:
- instalacao do pacote em modo editavel
- suite de testes unitarios

Ela roda automaticamente em:
- push para main
- push para branches codex/**
- pull_request

## 3. Teste de sintaxe

Verifica se os modulos Python compilam.
Comando:
python3 -m compileall src

## 4. Teste de instalacao

Com ambiente virtual ativo, execute:
pip install -e .
cowvision --help

## 5. Teste de banco

Garanta que o PostgreSQL esta no ar e rode:
cowvision init-db

Depois verifique se as tabelas existem com o comando do psql:
\dt

Voce deve ver:
- calibrations
- measurements

## 6. Teste sem hardware

Captura:
cowvision capture-frame --backend mock

Calibracao:
cowvision calibrate --image referencia.png --point-a 100,200 --point-b 500,200 --distance-m 2.0 --name teste-mock

Medicao unica:
cowvision measure-once --backend mock

Monitoramento:
cowvision monitor --backend mock --frames 50 --interval 0.2

## 7. Teste com hardware real

Instale o backend correto:
- freenect para Kinect classico
- pykinect2 para Kinect v2

Teste captura:
cowvision capture-frame --backend freenect
ou
cowvision capture-frame --backend pykinect2

Faça calibracao com regua real:
cowvision calibrate --point-a 120,300 --point-b 620,300 --distance-m 2.0 --name baia-real

Execute medicao:
cowvision measure-once --backend freenect

## 8. Checklist de aceite

O projeto pode ser considerado funcional quando:
- testes unitarios passam
- instala sem erro
- cria banco sem erro
- captura frame no modo mock
- grava calibracao no banco
- salva preview de calibracao
- salva imagem anotada de medicao
- salva visualizacao de profundidade
- grava medicao no banco

## 9. Problemas comuns

Erro de conexao com banco:
- usuario
- senha
- host
- porta
- nome do banco

measure-once retorna no-object-detected:
- se existe calibracao salva
- se PIXELS_PER_METER esta configurado
- se o objeto tem area suficiente

Sem profundidade:
- backend nao entregou frame de profundidade
- hardware nao esta pronto
- biblioteca nao esta instalada corretamente

## 10. Sugestao de proximo passo

Quando quiser, eu posso montar tambem:
- dados de exemplo
- script SQL para criar banco e usuario
- script shell para subir o ambiente mais rapido
