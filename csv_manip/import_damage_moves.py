"""Importa da PokéAPI todos os golpes que causam dano para um CSV novo."""

import argparse
import csv
import json
import os
import tempfile
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


API_URL = "https://pokeapi.co/api/v2/move"
COLUNAS = [
    "id",
    "name",
    "type",
    "damage_class",
    "power",
    "accuracy",
    "pp",
    "priority",
    "generation",
    "target",
    "accuracy_below_100",
    "pokemon_row_indexes",
]


def criar_sessao() -> requests.Session:
    """Cria uma sessão que tenta novamente em caso de falhas temporárias."""
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    sessao = requests.Session()
    sessao.headers["User-Agent"] = "Pokelearn damage-moves importer"
    sessao.mount("https://", HTTPAdapter(max_retries=retry))
    return sessao


def buscar_json(sessao: requests.Session, url: str) -> dict[str, Any]:
    resposta = sessao.get(url, timeout=20)
    resposta.raise_for_status()
    return resposta.json()


def transformar_golpe(
    golpe: dict[str, Any],
    indices_por_nome: dict[str, list[int]] | None = None,
) -> dict[str, Any] | None:
    """Retorna uma linha somente para golpes de dano com poder numérico."""
    classe = golpe["damage_class"]["name"]
    poder = golpe["power"]
    if classe not in {"physical", "special"} or not poder or poder <= 0:
        return None

    precisao = golpe["accuracy"]
    indices_por_nome = indices_por_nome or {}
    indices_pokemon = set()
    for pokemon in golpe.get("learned_by_pokemon", []):
        nome = pokemon["name"].casefold()
        indices = indices_por_nome.get(nome, [])
        # A PokéAPI chama algumas formas-base de *-male, enquanto o CSV usa
        # apenas o nome da espécie (frillish, jellicent e pyroar).
        if not indices and nome.endswith("-male"):
            indices = indices_por_nome.get(nome.removesuffix("-male"), [])
        indices_pokemon.update(indices)

    return {
        "id": golpe["id"],
        "name": golpe["name"],
        "type": golpe["type"]["name"],
        "damage_class": classe,
        "power": poder,
        # Accuracy vazia indica que o golpe não usa o teste normal de precisão.
        "accuracy": "" if precisao is None else precisao,
        "pp": golpe["pp"],
        "priority": golpe["priority"],
        "generation": golpe["generation"]["name"],
        "target": golpe["target"]["name"],
        "accuracy_below_100": precisao is not None and precisao < 100,
        # Array JSON de índices de linha (base 0, sem contar o cabeçalho).
        "pokemon_row_indexes": json.dumps(sorted(indices_pokemon)),
    }


def carregar_indices_pokemon(caminho_pokemon: str) -> dict[str, list[int]]:
    indices_por_nome: dict[str, list[int]] = {}
    with open(caminho_pokemon, encoding="utf-8-sig", newline="") as arquivo:
        for indice, pokemon in enumerate(csv.DictReader(arquivo)):
            nome = pokemon["Name"].strip().casefold()
            indices_por_nome.setdefault(nome, []).append(indice)
    return indices_por_nome


def importar_golpes(caminho_saida: str, caminho_pokemon: str) -> int:
    sessao = criar_sessao()
    indices_por_nome = carregar_indices_pokemon(caminho_pokemon)
    listagem = buscar_json(sessao, f"{API_URL}?limit=100000&offset=0")
    urls = [item["url"] for item in listagem["results"]]
    linhas = []

    for indice, url in enumerate(urls, start=1):
        linha = transformar_golpe(
            buscar_json(sessao, url), indices_por_nome
        )
        # Movimentos sem nenhum Pokémon correspondente no CSV não são úteis
        # para os minigames e não devem fazer parte do arquivo final.
        if linha is not None and linha["pokemon_row_indexes"] != "[]":
            linhas.append(linha)
        if indice % 100 == 0 or indice == len(urls):
            print(f"Processados {indice}/{len(urls)} movimentos...")

    linhas.sort(key=lambda linha: linha["id"])
    pasta_saida = os.path.dirname(os.path.abspath(caminho_saida))
    os.makedirs(pasta_saida, exist_ok=True)

    # Só substitui o destino depois que o CSV estiver completamente pronto.
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="",
        dir=pasta_saida,
        delete=False,
    ) as arquivo:
        caminho_temporario = arquivo.name
        escritor = csv.DictWriter(
            arquivo, fieldnames=COLUNAS, lineterminator="\n"
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
    caminho_pokemon_padrao = os.path.normpath(
        os.path.join(pasta_script, "..", "all_pokemon_data.csv")
    )
    parser = argparse.ArgumentParser(
        description="Cria um CSV com os golpes de dano da PokéAPI."
    )
    parser.add_argument(
        "--output",
        default=caminho_padrao,
        help=f"Arquivo CSV de saída (padrão: {caminho_padrao})",
    )
    parser.add_argument(
        "--pokemon-csv",
        default=caminho_pokemon_padrao,
        help="CSV usado para relacionar nomes de Pokémon aos índices de linha",
    )
    argumentos = parser.parse_args()

    quantidade = importar_golpes(argumentos.output, argumentos.pokemon_csv)
    print(f"Sucesso! {quantidade} golpes salvos em {argumentos.output}")


if __name__ == "__main__":
    main()
