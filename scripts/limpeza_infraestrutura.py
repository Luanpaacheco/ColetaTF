"""
pip install pandas
"""

import pandas as pd

INPUT_PATH = "Tabela_Escola_2025.csv"
OUTPUT_ESCOLAS = "infra_escolas_em_publico.csv"

# ---------------------------------------------------------------------------
# 1) Colunas que vamos ler do arquivo original (de ~300 para ~30)
# ---------------------------------------------------------------------------
COLS_ID = [
    "NU_ANO_CENSO", "CO_ENTIDADE", "NO_REGIAO", "SG_UF", "NO_UF",
    "TP_LOCALIZACAO", "TP_DEPENDENCIA", "TP_SITUACAO_FUNCIONAMENTO",
]

# Indica se a escola oferece Ensino Médio em alguma modalidade
COLS_OFERTA_MEDIO = [
    "IN_COMUM_MEDIO_MEDIO", "IN_COMUM_MEDIO_INTEGRADO", "IN_COMUM_MEDIO_FIC", "IN_COMUM_MEDIO_NORMAL",
    "IN_ESP_EXCLUSIVA_MEDIO_MEDIO", "IN_ESP_EXCLUSIVA_MEDIO_INTEGR", "IN_ESP_EXCLUSIVA_MEDIO_FIC",
    "IN_ESP_EXCLUSIVA_MEDIO_NORMAL",
]

# Indicadores de infraestrutura selecionados (saneamento, espaços pedagógicos,
# tecnologia e acessibilidade) - um recorte representativo, não as ~150 colunas
# de infraestrutura disponíveis no Censo Escolar completo.
COLS_INFRA = [
    "IN_AGUA_POTAVEL", "IN_ENERGIA_REDE_PUBLICA", "IN_ESGOTO_REDE_PUBLICA", "IN_LIXO_SERVICO_COLETA",
    "IN_BIBLIOTECA", "IN_BIBLIOTECA_SALA_LEITURA", "IN_LABORATORIO_CIENCIAS", "IN_LABORATORIO_INFORMATICA",
    "IN_QUADRA_ESPORTES", "IN_REFEITORIO", "IN_INTERNET", "IN_INTERNET_ALUNOS", "IN_COMPUTADOR",
    "IN_ACESSIBILIDADE_RAMPAS", "IN_BANHEIRO_PNE", "IN_ALIMENTACAO", "IN_SALA_LEITURA", "IN_AUDITORIO",
]

usecols = COLS_ID + COLS_OFERTA_MEDIO + COLS_INFRA

# ---------------------------------------------------------------------------
# 2) Leitura do arquivo (encoding latin1, separador ";")
# ---------------------------------------------------------------------------
df = pd.read_csv(INPUT_PATH, sep=";", encoding="latin1", usecols=usecols, low_memory=False)

# ---------------------------------------------------------------------------
# 3) Filtros
# ---------------------------------------------------------------------------
# 3.1 - Apenas escolas em atividade
df = df[df["TP_SITUACAO_FUNCIONAMENTO"] == 1].copy()

# 3.2 - Apenas escolas públicas (Federal=1, Estadual=2, Municipal=3; exclui Privada=4)
df = df[df["TP_DEPENDENCIA"].isin([1, 2, 3])].copy()

# 3.3 - Apenas escolas que oferecem Ensino Médio em alguma modalidade
oferece_medio = (df[COLS_OFERTA_MEDIO].fillna(0).sum(axis=1) > 0)
df = df[oferece_medio].copy()

# ---------------------------------------------------------------------------
# 4) Traduz códigos do INEP para texto
# ---------------------------------------------------------------------------
mapa_dependencia = {1: "Federal", 2: "Estadual", 3: "Municipal"}
mapa_localizacao = {1: "Urbana", 2: "Rural"}

df["dependencia"] = df["TP_DEPENDENCIA"].map(mapa_dependencia)
df["localizacao"] = df["TP_LOCALIZACAO"].map(mapa_localizacao)
df = df.rename(columns={"NU_ANO_CENSO": "ano", "NO_REGIAO": "regiao", "SG_UF": "sigla_uf", "NO_UF": "unidade_geografica"})

# ---------------------------------------------------------------------------
# 5) Seleciona e organiza colunas finais (nível escola)
# ---------------------------------------------------------------------------
df_final = df[["ano", "regiao", "sigla_uf", "unidade_geografica", "localizacao", "dependencia", "CO_ENTIDADE"] + COLS_INFRA].copy()
df_final[COLS_INFRA] = df_final[COLS_INFRA].fillna(0).astype(int)

df_final.to_csv(OUTPUT_ESCOLAS, index=False, encoding="utf-8-sig")

# ---------------------------------------------------------------------------
# 6) Resumo no console
# ---------------------------------------------------------------------------
print("=== Limpeza concluída ===")
print(f"Escolas públicas de Ensino Médio em atividade: {len(df_final)}")
print(f"\nDistribuição por região:\n{df_final['regiao'].value_counts()}")
print(f"\nArquivo salvo: {OUTPUT_ESCOLAS}")
