import csv
import os


# Os valores de saída são exatamente as chaves usadas em type_data.py.
# Também aceitamos traduções antigas para que o script possa migrar o CSV atual.
TRADUCAO_TIPOS = {
    "normal": "Normal",
    "fire": "Fogo", "fogo": "Fogo",
    "water": "Água", "água": "Água",
    "electric": "Elétrico", "elétrico": "Elétrico",
    "grass": "Grama", "grama": "Grama",
    "ice": "Gelo", "gelo": "Gelo",
    "fighting": "Lutador", "lutador": "Lutador",
    "poison": "Venenoso", "veneno": "Venenoso", "venenoso": "Venenoso",
    "ground": "Terra", "terrestre": "Terra", "terra": "Terra",
    "flying": "Voador", "voador": "Voador",
    "psychic": "Psíquico", "psíquico": "Psíquico",
    "bug": "Inseto", "inseto": "Inseto",
    "rock": "Pedra", "pedra": "Pedra",
    "ghost": "Fantasma", "fantasma": "Fantasma",
    "dragon": "Dragão", "dragão": "Dragão",
    "dark": "Sombrio", "sombrio": "Sombrio",
    "steel": "Metal", "metal": "Metal",
    "fairy": "Fada", "fada": "Fada",
}


def traduzir_tipos():
    pasta_script = os.path.dirname(os.path.abspath(__file__))
    caminho_csv = os.path.normpath(
        os.path.join(pasta_script, "..", "data", "all_pokemon_data.csv")
    )

    with open(caminho_csv, encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        nomes_colunas = leitor.fieldnames
        linhas = list(leitor)

    colunas_tipo = ["Primary Typing", "Secondary Typing"]
    for linha in linhas:
        for coluna in colunas_tipo:
            tipo = linha[coluna].strip()
            if tipo:
                linha[coluna] = TRADUCAO_TIPOS.get(tipo.casefold(), tipo)

    with open(caminho_csv, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(
            arquivo, fieldnames=nomes_colunas, lineterminator="\n"
        )
        escritor.writeheader()
        escritor.writerows(linhas)

    print("Sucesso! Os tipos foram normalizados para a tabela do app.")


if __name__ == "__main__":
    traduzir_tipos()
