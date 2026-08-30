import altair as alt
import streamlit as st

from carregadores import carregar_dataframes
from medidas import ANO_ANALISE, calcular_indicadores


st.set_page_config(page_title="Panorama da Saúde Suplementar", page_icon="📊", layout="wide")


@st.cache_data
def carregar_dados():
    return carregar_dataframes()


_, cadop_canceladas, empresas_plano_saude, acidentes = carregar_dados()
indicadores = calcular_indicadores(cadop_canceladas, empresas_plano_saude, acidentes)

st.title("Análise Planos de saude e Acidentes de Trabalho")
st.caption(f"Indicadores e evolução mensal — ano de referência: {ANO_ANALISE}")

coluna_1, coluna_2, coluna_3, coluna_4 = st.columns(4)
coluna_1.metric("Operadoras em atividade", f"{indicadores.operadoras_em_atividade:,}".replace(",", "."))
coluna_2.metric("Novas operadoras", f"{indicadores.novas_operadoras:,}".replace(",", "."), f"em {ANO_ANALISE}")
coluna_3.metric("Operadoras que fecharam", f"{indicadores.operadoras_que_fecharam:,}".replace(",", "."), f"em {ANO_ANALISE}")
coluna_4.metric("Acidentes no ano", f"{indicadores.acidentes_no_ano:,}".replace(",", "."), f"em {ANO_ANALISE}")


def grafico_linha(dados, eixo_y, titulo, cor):
    return (
        alt.Chart(dados, title=titulo)
        .mark_line(point=True, color=cor, strokeWidth=3)
        .encode(
            x=alt.X("Mês:T", title=None, axis=alt.Axis(format="%b/%Y", labelAngle=-35)),
            y=alt.Y(f"{eixo_y}:Q", title=None),
            tooltip=[alt.Tooltip("Mês:T", title="Mês", format="%B de %Y"), alt.Tooltip(f"{eixo_y}:Q", title=eixo_y)],
        )
        .properties(height=290)
    )


linha_1, linha_2 = st.columns(2)
with linha_1:
    st.altair_chart(grafico_linha(indicadores.novas_operadoras_por_mes, "Novas operadoras", "Evolução mensal de novas operadoras", "#127C8A"), width="stretch")
with linha_2:
    st.altair_chart(grafico_linha(indicadores.saidas_operadoras_por_mes, "Operadoras que fecharam", "Evolução mensal das saídas", "#E76F51"), width="stretch")

st.altair_chart(grafico_linha(indicadores.acidentes_por_mes, "Total de acidentes", "Evolução mensal de acidentes", "#3A86FF"), width="stretch")


coluna_modalidade, coluna_tipo = st.columns(2)
with coluna_modalidade:
    grafico_modalidade = (
        alt.Chart(indicadores.operadoras_por_modalidade, title="Operadoras em atividade por modalidade")
        .mark_bar(color="#127C8A", cornerRadiusEnd=4)
        .encode(x=alt.X("Total de operadoras:Q", title=None), y=alt.Y("Modalidade:N", sort="-x", title=None), tooltip=["Modalidade", "Total de operadoras"])
        .properties(height=290)
    )
    st.altair_chart(grafico_modalidade, width="stretch")

with coluna_tipo:
    grafico_tipo = (
        alt.Chart(indicadores.acidentes_por_tipo, title="Acidentes por tipo")
        .mark_arc(innerRadius=55)
        .encode(theta=alt.Theta("Total de acidentes:Q"), color=alt.Color("Tipo do Acidente:N", legend=alt.Legend(title=None)), tooltip=["Tipo do Acidente", "Total de acidentes"])
        .properties(height=290)
    )
    st.altair_chart(grafico_tipo, width="stretch")
