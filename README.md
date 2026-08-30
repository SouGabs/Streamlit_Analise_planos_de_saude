# Análise Planos de saude e Acidentes de Trabalho

Dashboard em Streamlit com indicadores de operadoras de planos de saúde e acidentes de trabalho em 2026.

## O que o dashboard apresenta

- Operadoras em atividade, novas operadoras e operadoras que fecharam;
- Total de acidentes no ano;
- Evolução mensal das entradas, saídas e acidentes;
- Mapa de acidentes por estado;
- Distribuição de operadoras por modalidade e acidentes por tipo.

## Estrutura do projeto

```text
.
├── app.py              # Interface e visuais Streamlit
├── carregadores.py     # Leitura dos arquivos CSV
├── medidas.py          # Transformações e indicadores
├── dados/              # Bases CSV usadas pelo dashboard
├── requirements.txt    # Dependências do projeto
└── README.md
```

## Como executar

Requer Python 3.10 ou superior.

```bash
python -m venv .venv
```

Ative o ambiente virtual e instale as dependências:

```bash
pip install -r requirements.txt
```

Inicie a aplicação:

```bash
streamlit run app.py
```

## Dados

As bases necessárias ficam na pasta `dados/`.
