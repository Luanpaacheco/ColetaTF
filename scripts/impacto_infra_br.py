import pandas as pd

base = pd.read_csv("base_escola_2024.csv")

infra_vars = {
    "IN_ENERGIA_REDE_PUBLICA": "Energia elétrica",
    "IN_AGUA_POTAVEL": "Água potável",
    "IN_COMPUTADOR": "Computador",
}
taxas = {
    "taxa_aprovacao": "Aprovação",
    "taxa_reprovacao": "Reprovação",
    "taxa_abandono": "Abandono",
}

# --- Tabela "com vs sem" cada item de infraestrutura ---
linhas = []
for col, nome_infra in infra_vars.items():
    for tcol, nome_taxa in taxas.items():
        medias = base.groupby(col)[tcol].mean()
        com, sem = medias.get(1), medias.get(0)
        linhas.append({
            "infraestrutura": nome_infra,
            "taxa": nome_taxa,
            "media_com": round(com, 2) if com is not None else None,
            "media_sem": round(sem, 2) if sem is not None else None,
            "diferenca_pp": round(com - sem, 2) if (com is not None and sem is not None) else None,
            "n_com": int((base[col] == 1).sum()),
            "n_sem": int((base[col] == 0).sum()),
        })

impacto = pd.DataFrame(linhas)
impacto.to_csv("impacto_infra_brasil_2024.csv", index=False, encoding="utf-8-sig")
print("=== IMPACTO (com vs sem) ===")
print(impacto.to_string(index=False))

# --- Índice de infraestrutura (0 a 3) ---
base["indice_infra"] = base[list(infra_vars)].sum(axis=1)
indice = base.groupby("indice_infra").agg(
    aprovacao_media=("taxa_aprovacao", "mean"),
    reprovacao_media=("taxa_reprovacao", "mean"),
    abandono_media=("taxa_abandono", "mean"),
    n_escolas=("CO_ENTIDADE", "count"),
).round(2).reset_index()
indice.to_csv("indice_infra_brasil_2024.csv", index=False, encoding="utf-8-sig")
print("\n=== ÍNDICE DE INFRA (0 a 3) ===")
print(indice.to_string(index=False))

# CRIA os csvs impacto_infra_brasil_2024.csv e indice_infra_brasil_2024.csv