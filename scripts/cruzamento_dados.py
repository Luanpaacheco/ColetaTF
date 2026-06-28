import pandas as pd

# --- Carrega taxas ---
rend = pd.read_excel("tx_rend_escolas_2024.xlsx", skiprows=8)  # ajuste o nome do arquivo

rend = rend.rename(columns={
    "1_CAT_MED": "taxa_aprovacao",
    "2_CAT_MED": "taxa_reprovacao",
    "3_CAT_MED": "taxa_abandono",
})

# Converte taxas para número (trata vírgula decimal e marcadores de "sem dado")
for c in ["taxa_aprovacao", "taxa_reprovacao", "taxa_abandono"]:
    rend[c] = pd.to_numeric(
        rend[c].astype(str).str.replace(",", ".").replace({"--": None, "": None, "nan": None}),
        errors="coerce"
    )

rend["CO_ENTIDADE"] = pd.to_numeric(rend["CO_ENTIDADE"], errors="coerce")

# --- Carrega infra e junta ---
infra = pd.read_csv("infra_escolas_em_publico.csv")
infra["CO_ENTIDADE"] = pd.to_numeric(infra["CO_ENTIDADE"], errors="coerce")

base = infra.merge(
    rend[["CO_ENTIDADE", "taxa_aprovacao", "taxa_reprovacao", "taxa_abandono"]],
    on="CO_ENTIDADE", how="inner"
)

# Remove escolas sem nenhuma taxa de Médio válida
base = base.dropna(subset=["taxa_aprovacao", "taxa_reprovacao", "taxa_abandono"], how="all")

base.to_csv("base_escola_2024.csv", index=False, encoding="utf-8-sig")

print(f"Infra (escolas):                {len(infra)}")
print(f"Após cruzamento e limpeza:      {len(base)}")
print(f"Perda no cruzamento:            {len(infra) - len(base)} escolas")
print()
print(base[["taxa_aprovacao", "taxa_reprovacao", "taxa_abandono"]].describe())

# Cria o csv base_escola_2024.csv, que será usado para análises de impacto da infraestrutura no desempenho.