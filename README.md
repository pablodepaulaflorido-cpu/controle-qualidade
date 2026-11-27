
# Controle de Qualidade Industrial com Python

Projeto de portfólio que simula uma rotina de inspeção industrial: lê medições de peças em CSV, identifica peças aprovadas e reprovadas, calcula estatísticas e gera arquivos de resultado.

## Objetivos

- Ler medições de `dados/medicoes.csv`.
- Classificar cada peça conforme a tolerância dimensional.
- Calcular quantidade, média, desvio padrão e percentual de reprovação.
- Calcular os índices de capabilidade **Cp e Cpk** por tipo.
- Exportar as peças aprovadas e reprovadas em arquivos CSV.
- Validar funções importantes com testes automatizados.

## Tecnologias

- Python 3.10 ou superior
- Biblioteca padrão: `csv`, `pathlib` e `collections`
- `pytest` para executar os testes (opcional)

## Estrutura do projeto

```text
controle_qualidade/
├── README.md
├── requirements.txt
├── dados/
│   └── medicoes.csv
└── src/
    ├── analise.py
    └── tests/
        └── test_analise.py
```

## Como executar

Abra o terminal na pasta principal do projeto e execute:

```bash
python src/analise.py
```

O programa cria/atualiza automaticamente `dados/aprovadas.csv` e `dados/reprovadas.csv`.

### Executar os testes

Instale a dependência de desenvolvimento:

```bash
python -m pip install -r requirements.txt
```

Depois rode:

```bash
python -m pytest -v
```

## Regra de aprovação

Uma peça é reprovada quando:

```text
|medida_mm - nominal_mm| > tolerancia_mm
```

A comparação arredonda a diferença e a tolerância para seis casas decimais, evitando que pequenos erros de representação de números decimais em ponto flutuante classifiquem incorretamente uma peça que está exatamente no limite. Portanto, uma peça exatamente no limite é aprovada.

## Indicadores e fórmulas

- **Média:** soma das medições dividida pela quantidade.
- **Desvio padrão amostral:** raiz quadrada da soma dos desvios ao quadrado dividida por `n - 1`.
- **Cp:** `(limite_superior - limite_inferior) / (6 × desvio padrão)`.
- **Cpk:** menor valor entre `(limite_superior - média) / (3 × desvio padrão)` e `(média - limite_inferior) / (3 × desvio padrão)`.

Os limites são calculados por `nominal ± tolerância`.

Cp mede a capacidade potencial considerando a dispersão, mas não considera o deslocamento da média em relação ao centro da especificação. Cpk considera também esse deslocamento. Por isso, Cpk é especialmente útil quando o processo está descentralizado.

**Atenção:** Cp/Cpk abaixo de 1,33 indicam que o processo não atende ao critério adotado neste projeto. Esses índices, calculados a partir desta amostra, não comprovam por si só que o processo esteja estatisticamente estável. Uma avaliação industrial completa também exige analisar estabilidade, sistema de medição e contexto do processo.

## Resultado esperado para o CSV fornecido

O arquivo de exemplo contém 120 medições:

- 108 peças aprovadas (90%).
- 12 peças reprovadas (10%).

| Tipo | Peças | Aprovadas | Reprovadas | Cp aproximado | Cpk aproximado |
|---|---:|---:|---:|---:|---:|
| EIXO-A | 40 | 37 | 3 | 0,522 | 0,520 |
| BUCHA-B | 40 | 34 | 6 | 0,695 | 0,449 |
| PINO-C | 40 | 37 | 3 | 0,537 | 0,522 |

Os índices estão abaixo de 1,33. A BUCHA-B apresenta Cpk mais baixo que Cp, indicando que a média está deslocada em direção ao limite superior.

Os resultados são calculados a partir dos dados fictícios fornecidos no projeto; não representam dados reais de uma empresa.

## Melhorias futuras

- Criar gráficos de distribuição e limites de especificação.
- Adicionar filtros por data e inspetor.
- Receber o caminho do CSV por argumento de linha de comando (`argparse`).
- Criar uma interface simples para consulta dos resultados.
- Investigar estabilidade do processo com cartas de controle.

