"""Adiciona a cada Pokémon os IDs dos golpes de dano que ele aprende."""

import argparse
import csv
import json
import os
import tempfile


NOME_COLUNA = "Damage Move IDs"


def adicionar_ids(
    caminho_pokemon: str,
    caminho_golpes: str,
    caminho_saida: str,
) -> int:
    with open(caminho_pokemon, encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        colunas = list(leitor.fieldnames or [])
        pokemon = list(leitor)

    ids_por_indice: list[set[int]] = [set() for _ in pokemon]
    with open(caminho_golpes, encoding="utf-8-sig", newline="") as arquivo:
        for golpe in csv.DictReader(arquivo):
            golpe_id = int(golpe["id"])
            indices = json.loads(golpe["pokemon_row_indexes"])
            if not isinstance(indices, list):
                raise ValueError(
                    f"pokemon_row_indexes inválido no golpe {golpe_id}"
                )
            for indice in indices:
                if not isinstance(indice, int) or not 0 <= indice < len(pokemon):
                    raise ValueError(
                        f"Índice {indice!r} inválido no golpe {golpe_id}"
                    )
                ids_por_indice[indice].add(golpe_id)

    if NOME_COLUNA not in colunas:
        colunas.append(NOME_COLUNA)
    for indice, linha in enumerate(pokemon):
        linha[NOME_COLUNA] = json.dumps(sorted(ids_por_indice[indice]))

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
        escritor.writerows(pokemon)

    os.replace(caminho_temporario, caminho_saida)
    return len(pokemon)


def main() -> None:
    pasta_script = os.path.dirname(os.path.abspath(__file__))
    raiz = os.path.normpath(os.path.join(pasta_script, ".."))
    caminho_pokemon = os.path.join(raiz, "all_pokemon_data.csv")
    caminho_golpes = os.path.join(raiz, "damage_moves.csv")

    parser = argparse.ArgumentParser(
        description="Adiciona IDs dos golpes aprendíveis ao CSV de Pokémon."
    )
    parser.add_argument("--pokemon-csv", default=caminho_pokemon)
    parser.add_argument("--moves-csv", default=caminho_golpes)
    parser.add_argument(
        "--output",
        default=caminho_pokemon,
        help="Saída; por padrão atualiza all_pokemon_data.csv",
    )
    argumentos = parser.parse_args()

    quantidade = adicionar_ids(
        argumentos.pokemon_csv,
        argumentos.moves_csv,
        argumentos.output,
    )
    print(
        f"Sucesso! A coluna '{NOME_COLUNA}' foi salva para "
        f"{quantidade} Pokémon em {argumentos.output}"
    )


if __name__ == "__main__":
    main()
