import csv
import os


# Migração dos nomes antigos/em inglês para o padrão usado pelo app.
TRADUCAO_GRUPOS_XP = {
    "fast": "Rápido",
    "rápido": "Rápido",
    "medium fast": "Médio-Rápido",
    "médio-rápido": "Médio-Rápido",
    "medium slow": "Médio-Lento",
    "médio-lento": "Médio-Lento",
    "slow": "Lento",
    "lento": "Lento",
    "erratic": "Errático",
    "errático": "Errático",
    "fluctuating": "Flutuante",
    "flutuante": "Flutuante",
}


def traduzir_grupos_xp():
    pasta_script = os.path.dirname(os.path.abspath(__file__))
    caminho_csv = os.path.normpath(
        os.path.join(pasta_script, "..", "data", "all_pokemon_data.csv")
    )

    with open(caminho_csv, encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        nomes_colunas = leitor.fieldnames
        linhas = list(leitor)

    for linha in linhas:
        grupo = linha["Experience Group"].strip()
        if grupo:
            linha["Experience Group"] = TRADUCAO_GRUPOS_XP.get(
                grupo.casefold(), grupo
            )

    with open(caminho_csv, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(
            arquivo, fieldnames=nomes_colunas, lineterminator="\n"
        )
        escritor.writeheader()
        escritor.writerows(linhas)

    print("Sucesso! Os grupos de XP foram traduzidos e normalizados.")


if __name__ == "__main__":
    traduzir_grupos_xp()
