"""
Dashboard - Infraestrutura escolar x Taxas de rendimento (Ensino Médio público, Brasil 2024)

Como rodar:
    pip install streamlit pandas plotly
    streamlit run app_educacao.py

Os três CSVs devem estar na MESMA pasta deste arquivo:
    - base_escola_2024.csv
    - impacto_infra_brasil_2024.csv
    - indice_infra_brasil_2024.csv
"""

import pathlib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Infraestrutura x Rendimento Escolar", layout="wide")

PASTA = pathlib.Path(__file__).parent

# Paleta consistente para as três taxas
COR_APROV = "#2E7D32"   # verde
COR_REPROV = "#F9A825"  # amarelo
COR_ABAND = "#C62828"   # vermelho


# ---------------------------------------------------------------------------
# Carregamento dos dados (cacheado)
# ---------------------------------------------------------------------------
@st.cache_data
def carregar():
    base = pd.read_csv(PASTA / "base_escola_2024.csv")
    impacto = pd.read_csv(PASTA / "impacto_infra_brasil_2024.csv")
    indice = pd.read_csv(PASTA / "indice_infra_brasil_2024.csv")
    return base, impacto, indice


try:
    base, impacto, indice = carregar()
except FileNotFoundError as e:
    st.error(f"Arquivo não encontrado: {e.filename}\n\n"
             f"Coloque os três CSVs na mesma pasta de app_educacao.py.")
    st.stop()


# ---------------------------------------------------------------------------
# Cabeçalho
# ---------------------------------------------------------------------------
st.title("Infraestrutura escolar e rendimento no Ensino Médio")
st.caption("Escolas públicas com Ensino Médio em atividade · Censo Escolar / INEP 2024 · "
           "as relações são associações, não impacto causal")

# ---------------------------------------------------------------------------
# KPIs de topo (nível Brasil)
# ---------------------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Escolas analisadas", f"{len(base):,}".replace(",", "."))
c2.metric("Aprovação média", f"{base['taxa_aprovacao'].mean():.1f}%")
c3.metric("Reprovação média", f"{base['taxa_reprovacao'].mean():.1f}%")
c4.metric("Abandono médio", f"{base['taxa_abandono'].mean():.1f}%")

st.divider()

# ---------------------------------------------------------------------------
# GRÁFICO 1 — Escada do índice de infraestrutura
# ---------------------------------------------------------------------------
st.subheader("1. Efeito acumulado: quanto mais infraestrutura, menor o abandono")

indice_plot = indice.copy()
indice_plot["indice_infra"] = indice_plot["indice_infra"].astype(str)

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=indice_plot["indice_infra"], y=indice_plot["abandono_media"],
    mode="lines+markers+text", name="Abandono",
    line=dict(color=COR_ABAND, width=3),
    text=[f"{v:.1f}%" for v in indice_plot["abandono_media"]],
    textposition="top center",
))
fig1.add_trace(go.Scatter(
    x=indice_plot["indice_infra"], y=indice_plot["aprovacao_media"],
    mode="lines+markers", name="Aprovação",
    line=dict(color=COR_APROV, width=2, dash="dot"),
))
fig1.update_layout(
    xaxis_title="Índice de infraestrutura (0 = nenhum recurso, 3 = energia + água + computador)",
    yaxis_title="Taxa média (%)",
    height=430, hovermode="x unified",
)
st.plotly_chart(fig1, use_container_width=True)

# Tamanho de amostra à mostra (o alerta de honestidade)
with st.expander("Tamanho de amostra por grupo (importante!)"):
    st.write("A maioria das escolas tem os três recursos. Os grupos com pouca "
             "infraestrutura são pequenos e atípicos — leia as taxas deles com cautela.")
    amostra = indice[["indice_infra", "n_escolas"]].copy()
    amostra["% do total"] = (amostra["n_escolas"] / amostra["n_escolas"].sum() * 100).round(1)
    st.dataframe(amostra, hide_index=True, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# GRÁFICO 2 — Com vs Sem cada item de infraestrutura
# ---------------------------------------------------------------------------
st.subheader("2. Escolas com vs sem cada recurso")

taxa_escolhida = st.radio(
    "Escolha a taxa:", ["Abandono", "Reprovação", "Aprovação"],
    horizontal=True,
)

imp = impacto[impacto["taxa"] == taxa_escolhida].copy()

# Transforma para formato longo (com / sem)
longo = imp.melt(
    id_vars=["infraestrutura", "n_com", "n_sem"],
    value_vars=["media_com", "media_sem"],
    var_name="condicao", value_name="valor",
)
longo["condicao"] = longo["condicao"].map({"media_com": "Tem o recurso",
                                           "media_sem": "Não tem"})

fig2 = px.bar(
    longo, x="infraestrutura", y="valor", color="condicao",
    barmode="group", text_auto=".1f",
    color_discrete_map={"Tem o recurso": "#1565C0", "Não tem": "#B0BEC5"},
    labels={"infraestrutura": "", "valor": f"Taxa de {taxa_escolhida.lower()} (%)",
            "condicao": ""},
)
fig2.update_layout(height=430)
st.plotly_chart(fig2, use_container_width=True)

# Tabela com diferença e amostra
st.caption("Diferença em pontos percentuais e número de escolas em cada grupo:")
tabela = imp[["infraestrutura", "media_com", "media_sem", "diferenca_pp", "n_com", "n_sem"]]
st.dataframe(tabela, hide_index=True, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# GRÁFICO 3 — Recorte por região (usa a base granular)
# ---------------------------------------------------------------------------
st.subheader("3. Comparação por região")

metrica = st.selectbox(
    "Métrica:",
    {"taxa_abandono": "Taxa de abandono",
     "taxa_reprovacao": "Taxa de reprovação",
     "taxa_aprovacao": "Taxa de aprovação"},
    format_func=lambda k: {"taxa_abandono": "Taxa de abandono",
                           "taxa_reprovacao": "Taxa de reprovação",
                           "taxa_aprovacao": "Taxa de aprovação"}[k],
)

por_regiao = (base.groupby("regiao")[metrica].mean()
              .sort_values(ascending=False).reset_index())

fig3 = px.bar(
    por_regiao, x="regiao", y=metrica, text_auto=".1f",
    labels={"regiao": "", metrica: "Taxa média (%)"},
    color=metrica, color_continuous_scale="Reds",
)
fig3.update_layout(height=430, coloraxis_showscale=False)
st.plotly_chart(fig3, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# GRÁFICO 4 — Filtro livre e exploração da base
# ---------------------------------------------------------------------------
st.subheader("4. Exploração livre")

col_a, col_b = st.columns(2)
regioes = col_a.multiselect("Regiões:", sorted(base["regiao"].unique()),
                            default=sorted(base["regiao"].unique()))
deps = col_b.multiselect("Dependência:", sorted(base["dependencia"].unique()),
                         default=sorted(base["dependencia"].unique()))

filtro = base[base["regiao"].isin(regioes) & base["dependencia"].isin(deps)]

st.write(f"**{len(filtro):,}** escolas no filtro atual."
         .replace(",", "."))

cc1, cc2, cc3 = st.columns(3)
cc1.metric("Aprovação", f"{filtro['taxa_aprovacao'].mean():.1f}%")
cc2.metric("Reprovação", f"{filtro['taxa_reprovacao'].mean():.1f}%")
cc3.metric("Abandono", f"{filtro['taxa_abandono'].mean():.1f}%")

with st.expander("Ver dados filtrados"):
    st.dataframe(filtro, use_container_width=True)