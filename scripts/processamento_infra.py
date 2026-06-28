import pandas as pd

INPUT_PATH = "microdados_ed_basica_2024.csv"   # ajuste o nome
OUTPUT_INFRA = "infra_escolas_em_publico.csv"

COLS_ID = ["NU_ANO_CENSO", "CO_ENTIDADE", "NO_REGIAO", "SG_UF", "NO_UF",
           "TP_LOCALIZACAO", "TP_DEPENDENCIA", "TP_SITUACAO_FUNCIONAMENTO"]

# Oferta de Médio regular: uma coluna só (substitui o bloco antigo)
COL_OFERTA_MEDIO = "IN_MED"

# As 3 variáveis de infra
COLS_INFRA = ["IN_ENERGIA_REDE_PUBLICA", "IN_AGUA_POTAVEL", "IN_COMPUTADOR"]

usecols = COLS_ID + [COL_OFERTA_MEDIO] + COLS_INFRA

df = pd.read_csv(INPUT_PATH, sep=";", encoding="latin1", usecols=usecols, low_memory=False)

# Filtros
df = df[df["TP_SITUACAO_FUNCIONAMENTO"] == 1].copy()      # em atividade
df = df[df["TP_DEPENDENCIA"].isin([1, 2, 3])].copy()      # públicas
df = df[df[COL_OFERTA_MEDIO] == 1].copy()                 # oferece Médio regular

# Traduções
df["dependencia"] = df["TP_DEPENDENCIA"].map({1: "Federal", 2: "Estadual", 3: "Municipal"})
df["localizacao"] = df["TP_LOCALIZACAO"].map({1: "Urbana", 2: "Rural"})
df = df.rename(columns={"NU_ANO_CENSO": "ano", "NO_REGIAO": "regiao",
                        "SG_UF": "sigla_uf", "NO_UF": "unidade_geografica"})

df_final = df[["ano", "regiao", "sigla_uf", "unidade_geografica",
               "localizacao", "dependencia", "CO_ENTIDADE"] + COLS_INFRA].copy()
df_final[COLS_INFRA] = df_final[COLS_INFRA].fillna(0).astype(int)
df_final.to_csv(OUTPUT_INFRA, index=False, encoding="utf-8-sig")

print(f"Escolas públicas com Ensino Médio em atividade: {len(df_final)}")
print(df_final["regiao"].value_counts())

#CRIA O CSV infra_escolas_em_publico.csv, que será usado para cruzamento com as taxas de rendimento.