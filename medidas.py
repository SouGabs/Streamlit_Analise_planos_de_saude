"""Métricas e transformações utilizadas no dashboard."""

from dataclasses import dataclass

import pandas as pd

ANO_ANALISE = 2026

# Coordenadas das capitais, usadas para posicionar os marcadores no mapa.
COORDENADAS_ESTADOS = {
    "Acre": (-9.9754, -67.8249), "Alagoas": (-9.6498, -35.7089),
    "Amapá": (0.0349, -51.0694), "Amazonas": (-3.1190, -60.0217),
    "Bahia": (-12.9714, -38.5014), "Ceará": (-3.7319, -38.5267),
    "Distrito Federal": (-15.7939, -47.8828), "Espírito Santo": (-20.3155, -40.3128),
    "Goiás": (-16.6869, -49.2648), "Maranhão": (-2.5387, -44.2825),
    "Mato Grosso": (-15.6014, -56.0979), "Mato Grosso do Sul": (-20.4697, -54.6201),
    "Minas Gerais": (-19.9167, -43.9345), "Pará": (-1.4558, -48.4902),
    "Paraíba": (-7.1195, -34.8450), "Paraná": (-25.4284, -49.2733),
    "Pernambuco": (-8.0476, -34.8770), "Piauí": (-5.0920, -42.8038),
    "Rio de Janeiro": (-22.9068, -43.1729), "Rio Grande Norte": (-5.7945, -35.2110),
    "Rio Grande do Norte": (-5.7945, -35.2110), "Rio Grande do Sul": (-30.0346, -51.2177),
    "Rondônia": (-8.7612, -63.9004), "Roraima": (2.8235, -60.6758),
    "Santa Catarina": (-27.5954, -48.5480), "São Paulo": (-23.5505, -46.6333),
    "Sergipe": (-10.9472, -37.0731), "Tocantins": (-10.1840, -48.3336),
}


@dataclass(frozen=True)
class IndicadoresDashboard:
    operadoras_em_atividade: int
    novas_operadoras: int
    operadoras_que_fecharam: int
    acidentes_no_ano: int
    novas_operadoras_por_mes: pd.DataFrame
    saidas_operadoras_por_mes: pd.DataFrame
    acidentes_por_mes: pd.DataFrame
    acidentes_por_estado: pd.DataFrame
    acidentes_sem_estado: int
    operadoras_por_modalidade: pd.DataFrame
    acidentes_por_tipo: pd.DataFrame


def _converter_data(serie: pd.Series, formato: str) -> pd.Series:
    """Converte texto em datas, ignorando valores inválidos."""
    return pd.to_datetime(serie, format=formato, errors="coerce")


def _contagem_distinta_por_mes(dados, coluna_data, coluna_registro, nome_total):
    return (
        dados.assign(Mês=dados[coluna_data].dt.to_period("M").dt.to_timestamp())
        .groupby("Mês", as_index=False)[coluna_registro]
        .nunique()
        .rename(columns={coluna_registro: nome_total})
        .sort_values("Mês")
    )


def _contagem_linhas_por_mes(dados, coluna_data, nome_total):
    return (
        dados.assign(Mês=dados[coluna_data].dt.to_period("M").dt.to_timestamp())
        .groupby("Mês", as_index=False)
        .size()
        .rename(columns={"size": nome_total})
        .sort_values("Mês")
    )


def calcular_indicadores(
    cadop_canceladas: pd.DataFrame,
    empresas_plano_saude: pd.DataFrame,
    acidentes: pd.DataFrame,
    ano: int = ANO_ANALISE,
) -> IndicadoresDashboard:
    """Calcula todos os KPIs e séries do dashboard, sem alterar as fontes."""
    ativas = empresas_plano_saude.copy()
    canceladas = cadop_canceladas.copy()
    acidentes_tratados = acidentes.copy()

    ativas["Data_Registro_ANS"] = _converter_data(ativas["Data_Registro_ANS"], "%Y-%m-%d")
    canceladas["Data_Descredenciamento"] = _converter_data(canceladas["Data_Descredenciamento"], "%Y-%m-%d")
    acidentes_tratados["Data Acidente"] = _converter_data(acidentes_tratados["Data Acidente"], "%d/%m/%Y")

    novas_no_ano = ativas.loc[ativas["Data_Registro_ANS"].dt.year.eq(ano)].dropna(subset=["Data_Registro_ANS"])
    saidas_no_ano = canceladas.loc[canceladas["Data_Descredenciamento"].dt.year.eq(ano)].dropna(subset=["Data_Descredenciamento"])
    acidentes_no_ano = acidentes_tratados.loc[acidentes_tratados["Data Acidente"].dt.year.eq(ano)].dropna(subset=["Data Acidente"])

    operadoras_por_modalidade = (
        ativas.assign(Modalidade=ativas["Modalidade"].fillna("Não informada").str.strip())
        .groupby("Modalidade", as_index=False)["REGISTRO_OPERADORA"]
        .nunique()
        .rename(columns={"REGISTRO_OPERADORA": "Total de operadoras"})
        .sort_values("Total de operadoras", ascending=False)
    )
    acidentes_por_tipo = (
        acidentes_no_ano.assign(**{"Tipo do Acidente": acidentes_no_ano["Tipo do Acidente"].fillna("Não informado").str.strip()})
        .groupby("Tipo do Acidente", as_index=False)
        .size()
        .rename(columns={"size": "Total de acidentes"})
        .sort_values("Total de acidentes", ascending=False)
    )
    acidentes_por_estado = (
        acidentes_no_ano.assign(
            Estado=acidentes_no_ano["UF  Munic.  Acidente"].fillna("").str.strip()
        )
        .groupby("Estado", as_index=False)
        .size()
        .rename(columns={"size": "Total de acidentes"})
    )
    acidentes_por_estado[["latitude", "longitude"]] = acidentes_por_estado["Estado"].map(
        COORDENADAS_ESTADOS
    ).apply(pd.Series)
    acidentes_sem_estado = int(acidentes_por_estado.loc[
        acidentes_por_estado["latitude"].isna(), "Total de acidentes"
    ].sum())
    acidentes_por_estado = acidentes_por_estado.dropna(subset=["latitude", "longitude"])
    # O parâmetro ``size`` de st.map representa metros. A raiz quadrada evita
    # que estados com muitos registros ocultem os demais marcadores.
    acidentes_por_estado["Tamanho do marcador"] = (
        acidentes_por_estado["Total de acidentes"].pow(0.5) * 3500
    ).round()

    return IndicadoresDashboard(
        operadoras_em_atividade=ativas["REGISTRO_OPERADORA"].nunique(),
        novas_operadoras=novas_no_ano["REGISTRO_OPERADORA"].nunique(),
        operadoras_que_fecharam=saidas_no_ano["REGISTRO_OPERADORA"].nunique(),
        acidentes_no_ano=len(acidentes_no_ano),
        novas_operadoras_por_mes=_contagem_distinta_por_mes(novas_no_ano, "Data_Registro_ANS", "REGISTRO_OPERADORA", "Novas operadoras"),
        saidas_operadoras_por_mes=_contagem_distinta_por_mes(saidas_no_ano, "Data_Descredenciamento", "REGISTRO_OPERADORA", "Operadoras que fecharam"),
        acidentes_por_mes=_contagem_linhas_por_mes(acidentes_no_ano, "Data Acidente", "Total de acidentes"),
        acidentes_por_estado=acidentes_por_estado,
        acidentes_sem_estado=acidentes_sem_estado,
        operadoras_por_modalidade=operadoras_por_modalidade,
        acidentes_por_tipo=acidentes_por_tipo,
    )
