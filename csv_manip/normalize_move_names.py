"""Normaliza a capitalização dos nomes em damage_moves.csv."""

import argparse
import csv
import os
import tempfile


def capitalizar_primeira_letra(nome: str) -> str:
    """Coloca a primeira letra em maiúscula sem alterar o restante."""
    nome = nome.strip()
    return nome[:1].upper() + nome[1:]


def normalizar_nomes(caminho_csv: str, caminho_saida: str) -> int:
    with open(caminho_csv, encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        colunas = list(leitor.fieldnames or [])
        linhas = list(leitor)

    if "name" not in colunas:
        raise ValueError("A coluna 'name' não foi encontrada no CSV.")

    for linha in linhas:
        linha["name"] = capitalizar_primeira_letra(linha["name"])

    pasta_saida = os.path.dirname(os.path.abspath(caminho_saida))
    os.makedirs(pasta_saida, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="",
        dir=pasta_saida,
        delete=False,
    ) as arquivo:
        caminho_temporario = arquivo.name
        escritor = csv.DictWriter(
            arquivo, fieldnames=colunas, lineterminator="\n"
        )
        escritor.writeheader()
        escritor.writerows(linhas)

    os.replace(caminho_temporario, caminho_saida)
    return len(linhas)


def main() -> None:
    pasta_script = os.path.dirname(os.path.abspath(__file__))
    caminho_padrao = os.path.normpath(
        os.path.join(pasta_script, "..", "damage_moves.csv")
    )

    parser = argparse.ArgumentParser(
        description="Capitaliza a primeira letra dos nomes dos golpes."
    )
    parser.add_argument("--input", default=caminho_padrao)
    parser.add_argument(
        "--output",
        default=caminho_padrao,
        help="Saída; por padrão atualiza damage_moves.csv",
    )
    argumentos = parser.parse_args()

    quantidade = normalizar_nomes(argumentos.input, argumentos.output)
    print(
        f"Sucesso! {quantidade} nomes normalizados em "
        f"{argumentos.output}"
    )


if __name__ == "__main__":
    main()
