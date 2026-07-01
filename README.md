# ColetaTF

Este repositório reúne dois scripts de limpeza e filtragem de dados do Censo Escolar/INEP.

Os datasets brutos não foram enviados para o GitHub por serem arquivos grandes e pesados para versionamento. Cada script espera que o arquivo de entrada esteja disponível localmente na mesma pasta de execução.

## Script 1: `scripts/limpeza_dados.py`

Lê o arquivo `tx_rend_brasil_regioes_ufs_2025.ods` e gera `tx_rendimento_em_publico_2025.csv`.

O que o script faz:

- Mantém apenas escolas públicas.
- Considera somente as colunas de Ensino Médio.
- Remove os detalhes por série e mantém apenas as taxas totais de:
  - aprovação
  - reprovação
  - abandono
- Adiciona a coluna `regiao` para cada UF, além de identificar Brasil e região quando aplicável.

## Script 2: `scripts/limpeza_infraestrutura.py`

Lê o arquivo `Tabela_Escola_2025.csv` e gera `infra_escolas_em_publico.csv`.

O que o script faz:

- Mantém apenas escolas em atividade.
- Mantém apenas escolas públicas.
- Mantém apenas escolas que oferecem Ensino Médio.
- Reduz o arquivo original para um conjunto menor de colunas de identificação e infraestrutura.
- Adiciona a coluna `regiao` para cada escola.

## Dependências

- `pandas`
- `numpy` para o script de rendimento
- `odfpy` para leitura do arquivo `.ods`

Instalação sugerida:

```bash
pip install pandas numpy odfpy
```

## Como executar

Execute os scripts a partir da pasta `scripts/`, garantindo que os arquivos de entrada estejam disponíveis no mesmo diretório ou com o caminho ajustado no código.

```bash
python limpeza_dados.py
python limpeza_infraestrutura.py
```

## Arquivos gerados

- `tx_rendimento_em_publico_2025.csv`
- `infra_escolas_em_publico.csv`
