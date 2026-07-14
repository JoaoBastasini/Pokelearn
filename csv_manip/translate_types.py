import os

import pandas as pd


TRADUCAO_TIPOS = {
    "normal": "normal",
    "fire": "fogo",
    "water": "água",
    "electric": "elétrico",
    "grass": "grama",
    "ice": "gelo",
    "fighting": "lutador",
    "poison": "veneno",
    "ground": "terrestre",
    "flying": "voador",
    "psychic": "psíquico",
    "bug": "inseto",
    "rock": "pedra",
    "ghost": "fantasma",
    "dragon": "dragão",
    "dark": "sombrio",
    "steel": "metal",
    "fairy": "fada",
}


def traduzir_tipos():
    pasta_script = os.path.dirname(os.path.abspath(__file__))
    caminho_csv = os.path.join(pasta_script, "..", "all_pokemon_data.csv")
    caminho_csv = os.path.normpath(caminho_csv)

    df_local = pd.read_csv(caminho_csv)
    colunas_tipo = ["Primary Typing", "Secondary Typing"]

    for coluna in colunas_tipo:
        # replace troca apenas valores completos da coluna, nunca partes de textos.
        df_local[coluna] = df_local[coluna].replace(TRADUCAO_TIPOS)

    df_local.to_csv(caminho_csv, index=False)
    print("Sucesso! Os tipos primario e secundario foram traduzidos.")


if __name__ == "__main__":
    traduzir_tipos()
