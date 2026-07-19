"""Traduz nome, tipo e classe dos golpes no damage_moves.csv."""

import argparse
import csv
import json
import os
import sys
import tempfile
import time

from deep_translator import GoogleTranslator


# Permite usar a fonte canônica de tipos mesmo quando este arquivo é executado
# diretamente a partir da pasta csv_manip.
RAIZ_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ_PROJETO not in sys.path:
    sys.path.insert(0, RAIZ_PROJETO)

from data.type_data import TYPE_CHART_OFFENSIVE


TRADUCAO_TIPOS = {
    "normal": "Normal",
    "fire": "Fogo",
    "water": "Água",
    "electric": "Elétrico",
    "grass": "Grama",
    "ice": "Gelo",
    "fighting": "Lutador",
    "poison": "Venenoso",
    "ground": "Terra",
    "flying": "Voador",
    "psychic": "Psíquico",
    "bug": "Inseto",
    "rock": "Pedra",
    "ghost": "Fantasma",
    "dragon": "Dragão",
    "dark": "Sombrio",
    "steel": "Metal",
    "fairy": "Fada",
}

TIPOS_DO_PROJETO = frozenset(TYPE_CHART_OFFENSIVE)

TRADUCAO_CLASSES = {
    "physical": "Físico",
    "special": "Especial",
}

# Traduções automáticas que perdem o sentido no contexto de uma batalha.
# Este glossário tem prioridade sobre o serviço externo e também é aplicado
# retroativamente a arquivos que já tenham sido traduzidos.
REVISOES_NOMES = {
    "accelerock": "Acelerrocha",
    "aerial-ace": "Ás dos Ares",
    "air-slash": "Corte de Ar",
    "aqua-tail": "Cauda Aquática",
    "arm-thrust": "Estocada de Braço",
    "assurance": "Revide",
    "astonish": "Assustar",
    "baddy-bad": "Maldade Máxima",
    "bind": "Constrição",
    "blast-burn": "Queimadura Explosiva",
    "blue-flare": "Chama Azul",
    "body-press": "Prensa Corporal",
    "bolt-beak": "Bico Elétrico",
    "bolt-strike": "Golpe Elétrico",
    "bone-club": "Clava de Osso",
    "boomburst": "Estrondo",
    "brave-bird": "Ave Brava",
    "breaking-swipe": "Varredura Quebradora",
    "bug-buzz": "Zumbido de Inseto",
    "bulldoze": "Terraplenagem",
    "burn-up": "Queima Total",
    "ceaseless-edge": "Corte Incessante",
    "chatter": "Tagarelar",
    "chip-away": "Desgastar",
    "circle-throw": "Arremesso Circular",
    "clanging-scales": "Escamas Ressonantes",
    "clear-smog": "Fumaça Clara",
    "core-enforcer": "Núcleo Punitivo",
    "crunch": "Mordida",
    "dark-pulse": "Pulso Sombrio",
    "darkest-lariat": "Laço Sombrio",
    "double-edge": "Investida Dupla",
    "double-iron-bash": "Pancada Dupla de Ferro",
    "drain-punch": "Soco Drenagem",
    "drill-peck": "Bicada Broca",
    "drill-run": "Broca Rápida",
    "fell-stinger": "Ferrão Mortal",
    "fishious-rend": "Mordida Branquial",
    "flare-blitz": "Investida Flamejante",
    "flash-cannon": "Canhão de Luz",
    "flip-turn": "Virada Rápida",
    "flying-press": "Prensa Voadora",
    "force-palm": "Palma da Força",
    "freeze-dry": "Congelamento a Seco",
    "fury-swipes": "Arranhões Furiosos",
    "fusion-bolt": "Raio de Fusão",
    "fusion-flare": "Chama de Fusão",
    "gigaton-hammer": "Martelo Gigaton",
    "glaive-rush": "Investida de Glaive",
    "hex": "Maldição",
    "high-jump-kick": "Chute de Salto Alto",
    "hydro-pump": "Hidrobomba",
    "hyper-beam": "Hiper-raio",
    "ice-punch": "Soco de Gelo",
    "icicle-crash": "Queda de Gelo",
    "ivy-cudgel": "Clava de Hera",
    "knock-off": "Desarme",
    "leech-life": "Sanguessuga",
    "mach-punch": "Soco Mach",
    "matcha-gotcha": "Pegadinha de Matcha",
    "meteor-mash": "Soco Meteoro",
    "moongeist-beam": "Raio Espectral",
    "night-slash": "Corte Noturno",
    "nuzzle": "Choque Carinhoso",
    "overdrive": "Sobrecarga",
    "pin-missile": "Míssil de Espinhos",
    "pollen-puff": "Bola de Pólen",
    "pound": "Pancada",
    "power-trip": "Arrogância",
    "psycho-boost": "Psicoimpulso",
    "psycho-cut": "Psicocorte",
    "psyshield-bash": "Golpe Psicoescudo",
    "psyshock": "Psicochoque",
    "psystrike": "Psicoataque",
    "rollout": "Rolamento",
    "round": "Eco",
    "scale-shot": "Tiro de Escamas",
    "seed-flare": "Clarão de Sementes",
    "shadow-sneak": "Sombra Furtiva",
    "skitter-smack": "Golpe Rastejante",
    "sky-uppercut": "Gancho Celeste",
    "slam": "Pancada Pesada",
    "slash": "Corte",
    "sludge": "Lodo",
    "sludge-bomb": "Bomba de Lodo",
    "sludge-wave": "Onda de Lodo",
    "smack-down": "Abater",
    "smog": "Fumaça",
    "spacial-rend": "Corte Espacial",
    "steel-beam": "Feixe de Aço",
    "stone-edge": "Lâmina de Pedra",
    "struggle-bug": "Esforço de Inseto",
    "sucker-punch": "Golpe Baixo",
    "sunsteel-strike": "Golpe Solar de Aço",
    "surging-strikes": "Golpes Fluentes",
    "swift": "Estrelas Velozes",
    "tackle": "Investida",
    "take-down": "Derrubada",
    "thrash": "Agitação",
    "throat-chop": "Golpe na Garganta",
    "triple-axel": "Axel Triplo",
    "twineedle": "Agulha Dupla",
    "u-turn": "Retorno",
    "v-create": "Gerador V",
    "vice-grip": "Aperto",
    "volt-switch": "Troca Voltaica",
    "volt-tackle": "Investida Voltaica",
    "wake-up-slap": "Tapa Despertador",
    "water-gun": "Jato d'Água",
    "water-spout": "Esguicho d'Água",
    "whirlpool": "Redemoinho",
    "x-scissor": "Tesoura X",
    "zap-cannon": "Canhão Elétrico",
}


def carregar_cache(caminho: str) -> dict[str, str]:
    if not os.path.exists(caminho):
        return {}
    with open(caminho, encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    if not isinstance(dados, dict):
        raise ValueError("O cache de traduções precisa ser um objeto JSON.")
    return {str(chave): str(valor) for chave, valor in dados.items()}


def salvar_cache(caminho: str, cache: dict[str, str]) -> None:
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(cache, arquivo, ensure_ascii=False, indent=2, sort_keys=True)
        arquivo.write("\n")


def traduzir_com_tentativas(
    tradutor: GoogleTranslator,
    texto: str,
    tentativas: int = 5,
) -> str:
    for tentativa in range(1, tentativas + 1):
        try:
            return tradutor.translate(texto).strip()
        except Exception:
            if tentativa == tentativas:
                raise
            espera = tentativa * 2
            print(
                f"Falha temporária; nova tentativa em {espera}s...",
                flush=True,
            )
            time.sleep(espera)
    raise RuntimeError("Não foi possível traduzir o texto.")


def traduzir_moves(
    caminho_csv: str,
    caminho_saida: str,
    caminho_cache: str,
) -> int:
    with open(caminho_csv, encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        colunas = list(leitor.fieldnames or [])
        linhas = list(leitor)

    obrigatorias = {"name", "type", "damage_class"}
    ausentes = obrigatorias.difference(colunas)
    if ausentes:
        raise ValueError(f"Colunas ausentes no CSV: {sorted(ausentes)}")

    cache = carregar_cache(caminho_cache)

    # Atualiza nomes de arquivos já traduzidos antes de substituir os valores
    # antigos no cache.
    for linha in linhas:
        classe = linha["damage_class"].strip().casefold()
        if classe in TRADUCAO_CLASSES:
            continue
        for nome_original, nome_revisado in REVISOES_NOMES.items():
            if linha["name"] == cache.get(nome_original):
                linha["name"] = nome_revisado
                break

    cache.update(REVISOES_NOMES)
    salvar_cache(caminho_cache, cache)
    tradutor = GoogleTranslator(source="en", target="pt")

    for numero, linha in enumerate(linhas, start=1):
        tipo_original = linha["type"].strip()
        tipo_padrao = TRADUCAO_TIPOS.get(
            tipo_original.casefold(), tipo_original
        )
        if tipo_padrao not in TIPOS_DO_PROJETO:
            raise ValueError(
                f"Tipo incompatível com type_data.py na linha {numero}: "
                f"{tipo_original!r}"
            )
        linha["type"] = tipo_padrao

        classe_original = linha["damage_class"].strip().casefold()

        # Se a classe já está traduzida, a linha já passou por este script.
        if classe_original not in TRADUCAO_CLASSES:
            continue

        nome_original = linha["name"].strip()
        if nome_original not in cache:
            texto = nome_original.replace("-", " ")
            cache[nome_original] = traduzir_com_tentativas(tradutor, texto)
            salvar_cache(caminho_cache, cache)
            # Evita sobrecarregar o serviço com chamadas consecutivas.
            time.sleep(0.25)

        linha["name"] = cache[nome_original]
        linha["damage_class"] = TRADUCAO_CLASSES[classe_original]

        if numero % 50 == 0 or numero == len(linhas):
            print(
                f"Traduzidos {numero}/{len(linhas)} golpes...",
                flush=True,
            )

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
    raiz = os.path.normpath(os.path.join(pasta_script, ".."))
    caminho_csv = os.path.join(raiz, "data", "damage_moves.csv")
    caminho_cache = os.path.join(pasta_script, "move_name_translations.json")

    parser = argparse.ArgumentParser(
        description="Traduz name, type e damage_class do CSV de golpes."
    )
    parser.add_argument("--input", default=caminho_csv)
    parser.add_argument("--output", default=caminho_csv)
    parser.add_argument("--cache", default=caminho_cache)
    argumentos = parser.parse_args()

    quantidade = traduzir_moves(
        argumentos.input,
        argumentos.output,
        argumentos.cache,
    )
    print(f"Sucesso! {quantidade} golpes salvos em {argumentos.output}")


if __name__ == "__main__":
    main()
