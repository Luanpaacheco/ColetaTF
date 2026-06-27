"""
pip install pandas odfpy
"""

import numpy as np
import pandas as pd

INPUT_PATH = "tx_rend_brasil_regioes_ufs_2025.ods"
SHEET_NAME = "BRASIL_REGIOES_UFS_"
OUTPUT_PATH = "tx_rendimento_em_publico.csv"


# ---------------------------------------------------------------------------
# 1) Leitura do arquivo bruto
# ---------------------------------------------------------------------------
# header=None porque o arquivo do INEP tem várias linhas de título/cabeçalho
# mesclado antes dos dados de fato começarem.
raw = pd.read_excel(INPUT_PATH, engine="odf", sheet_name=SHEET_NAME, header=None)

# Os dados começam na linha 10 do arquivo (índice 9) e terminam antes do
# rodapé com a fonte ("Fonte: INEP/Censo Escolar...").
data = raw.iloc[9:596].copy().reset_index(drop=True)

# ---------------------------------------------------------------------------
# 2) Nomes das colunas (só as que vamos usar: identificação + Ensino Médio)
# ---------------------------------------------------------------------------
# Posição das colunas no arquivo original:
#   0-3   : Ano, Unidade Geográfica, Localização, Dependência Administrativa
#   16    : Taxa de Aprovação - Ensino Médio - Total
#   34    : Taxa de Reprovação - Ensino Médio - Total
#   52    : Taxa de Abandono - Ensino Médio - Total
data = data.iloc[:, [0, 1, 2, 3, 16, 34, 52]].copy()
data.columns = [
    "ano", "unidade_geografica", "localizacao", "dependencia",
    "taxa_aprovacao", "taxa_reprovacao", "taxa_abandono",
]

# ---------------------------------------------------------------------------
# 3) Filtra apenas Escolas Públicas
#    (já estamos olhando só as colunas de Ensino Médio desde o passo 2)
# ---------------------------------------------------------------------------
df = data[data["dependencia"] == "Pública"].copy()

# ---------------------------------------------------------------------------
# 4) Converte para numérico (trata "--" do INEP como dado ausente)
# ---------------------------------------------------------------------------
for c in ["taxa_aprovacao", "taxa_reprovacao", "taxa_abandono"]:
    df[c] = pd.to_numeric(df[c].replace("--", np.nan), errors="coerce")

# ---------------------------------------------------------------------------
# 5) Classificação geográfica (Brasil / Região / UF) + mapeamento UF -> Região
# ---------------------------------------------------------------------------
REGIOES = ["Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"]

UF_PARA_REGIAO = {
    "Rondônia": "Norte", "Acre": "Norte", "Amazonas": "Norte", "Roraima": "Norte",
    "Pará": "Norte", "Amapá": "Norte", "Tocantins": "Norte",
    "Maranhão": "Nordeste", "Piauí": "Nordeste", "Ceará": "Nordeste",
    "Rio Grande do Norte": "Nordeste", "Paraíba": "Nordeste", "Pernambuco": "Nordeste",
    "Alagoas": "Nordeste", "Sergipe": "Nordeste", "Bahia": "Nordeste",
    "Minas Gerais": "Sudeste", "Espírito Santo": "Sudeste",
    "Rio de Janeiro": "Sudeste", "São Paulo": "Sudeste",
    "Paraná": "Sul", "Santa Catarina": "Sul", "Rio Grande do Sul": "Sul",
    "Mato Grosso do Sul": "Centro-Oeste", "Mato Grosso": "Centro-Oeste",
    "Goiás": "Centro-Oeste", "Distrito Federal": "Centro-Oeste",
}


def classifica_nivel(unidade: str) -> str:
    if unidade == "Brasil":
        return "Brasil"
    if unidade in REGIOES:
        return "Região"
    return "UF"


df["nivel_geografico"] = df["unidade_geografica"].apply(classifica_nivel)
df["regiao"] = df["unidade_geografica"].map(UF_PARA_REGIAO)
df.loc[df["nivel_geografico"] == "Região", "regiao"] = df["unidade_geografica"]
df.loc[df["nivel_geografico"] == "Brasil", "regiao"] = "Brasil"

# Reordena colunas: identificação primeiro, taxas por último
df = df[[
    "ano", "unidade_geografica", "nivel_geografico", "regiao", "localizacao", "dependencia",
    "taxa_aprovacao", "taxa_reprovacao", "taxa_abandono",
]]

# ---------------------------------------------------------------------------
# 6) Salva o arquivo limpo (1 único CSV)
# ---------------------------------------------------------------------------
df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

# ---------------------------------------------------------------------------
# 7) Resumo no console
# ---------------------------------------------------------------------------
print("=== Limpeza concluída ===")
print(f"Linhas: {len(df)}")
print(f"Níveis geográficos presentes: {df['nivel_geografico'].unique().tolist()}")
print(f"Localizações presentes: {df['localizacao'].unique().tolist()}")
print(f"\nArquivo salvo: {OUTPUT_PATH}")
