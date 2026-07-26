from flask import Flask, render_template, request, jsonify
from livereload import Server
import json
import math
import pandas as pd
import numpy as np
import random
import os
from data.type_data import TYPE_CHART_OFFENSIVE, TYPE_CHART_DEFENSIVE

'''
Para rodar o servidor Flask:
1. Certifique-se de que você tem o Flask e o Pandas instalados: pip install Flask pandas
2. Execute este arquivo: python app.py
3. Acesse no navegador: http://127.0.0.1:5000/
'''

app = Flask(__name__)

# -------- Carregar Dados --------

# Carrega os dados de forma relativa à raiz do projeto, independentemente
# do diretório de onde o app é executado
PASTA_DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

try:
    caminho_csv = os.path.join(PASTA_DADOS, 'all_pokemon_data.csv')
    dados_pokemon = pd.read_csv(caminho_csv)
    print("Dados de Pokémon carregados com sucesso.")
except FileNotFoundError:
    print("ERRO: O arquivo all_pokemon_data.csv não foi encontrado. Verifique o caminho.")
    dados_pokemon = pd.DataFrame() # Cria um DataFrame vazio para evitar erros

try:
    caminho_csv = os.path.join(PASTA_DADOS, 'damage_moves.csv')
    dados_moves = pd.read_csv(caminho_csv)
    tipos_moves = set(dados_moves["type"].dropna().astype(str).str.strip())
    tipos_invalidos = tipos_moves.difference(TYPE_CHART_OFFENSIVE)
    if tipos_invalidos:
        raise ValueError("Tipos incompatíveis em damage_moves.csv: " f"{sorted(tipos_invalidos)}")
    print("Dados de Ataques carregados com sucesso.")
except FileNotFoundError:
    print("ERRO: O arquivo damage_moves.csv não foi encontrado. Verifique o caminho.")
    dados_moves = pd.DataFrame() # Cria um DataFrame vazio para evitar erros


# -------- Funções Lógicas dos Minigames --------

# Calcula o multiplicador de eficácia do tipo
def get_type_effectiveness(attack_type, defender_types):
    multiplier = 1.0
    for d_type in defender_types:
        # Primeiro .get retorna o dicionário do tipo de ataque
        # Segundo .get retorna o valor de eficácia contra o tipo defensor, no caso de dual type, entra nesse trecho duas vezes (for)
        # Se não tem nada no dicionário, o ataque é neutro, multiplicador 1
        effectiveness = TYPE_CHART_OFFENSIVE.get(attack_type, {}).get(d_type, 1.0)
        multiplier *= effectiveness
    return multiplier

# Escolhe aleatoriamente o atacante, defensor, níveis e ataque
def setup_battle(df, moves):
    
    # Escolhe os Pokémon
    # Faz um DF com um único elemento, que possua ataques
    # Reseta o índice, o original vira uma coluna chamada 'index' e o novo é 0
    # Seleciona o primeiro e único elemento com iloc[0]
    atacantes_com_golpes = df[df["Damage Move IDs"] != "[]"]
    attacker_data = atacantes_com_golpes.sample(1).reset_index().iloc[0]
    defender_data = df.sample(1).reset_index().iloc[0]
    
    # Sorteia os níveis dos Pokémon
    level_atk = random.randint(40, 60) # Níveis em uma faixa razoável

    # Garante que o nível do defensor fique entre 40 e 60 e a diferença seja no máximo 10
    # level_def = random.randint(max(40, level_atk - 10), min(60, level_atk + 10))
    # Aparentemente o nível do defensor não é usado no cálculo de dano, então foi comentado, mas caso venha a calhar, está aí

    # Escolhe um ataque que o pokémon atacante pode aprender
    many_move_ids = json.loads(attacker_data["Damage Move IDs"])
    move_id = random.choice(many_move_ids)
    move = moves.loc[moves["id"] == move_id].iloc[0]

    move_name = move["name"]
    base_power = int(move["power"])
    is_physical = move["damage_class"] == "Físico"

    if is_physical:
        atk_stat = attacker_data['Attack']
        def_stat = defender_data['Defense']
        atk_stat_name = 'Attack'
        def_stat_name = 'Defense'
    else:
        atk_stat = attacker_data['Special Attack']
        def_stat = defender_data['Special Defense']
        atk_stat_name = 'Special Attack'
        def_stat_name = 'Special Defense'

    # Escolhe o tipo do ataque
    attack_type = move["type"]

    # Armazena os tipos do Pokémon
    attacker_types = []
    attacker_types.append(attacker_data['Primary Typing'])
    if pd.notna(attacker_data['Secondary Typing']):
        attacker_types.append(attacker_data['Secondary Typing'])
    
    # Calcula modificadores
    stab_mod = 1.5 if attack_type in attacker_types else 1.0
    
    defender_types = []
    defender_types.append(defender_data['Primary Typing'])
    if pd.notna(defender_data['Secondary Typing']):
        defender_types.append(defender_data['Secondary Typing'])

    type_effectiveness = get_type_effectiveness(attack_type, defender_types)

    # Cálculo de dano base (sem Fator Aleatório)
    # Dano Base = [ ( (2 * Nível / 5) + 2 ) * Poder * (Atk / Def) / 50 ] + 2
    base_calc = (((2 * level_atk / 5) + 2) * base_power * (atk_stat / def_stat) / 50) + 2
    
    # Dano Final Mínimo e Máximo (inclui STAB e Eficácia)
    # A resposta correta para o usuário será o Dano Máximo (fator aleatório = 1.0)
    damage_max = np.floor(base_calc * stab_mod * type_effectiveness * 1.00)
    damage_min = np.floor(base_calc * stab_mod * type_effectiveness * 0.85)


    # Agrupa Info

    attacker = {
        "attacker_name": attacker_data['Name'],
        "attacker_image_url": attacker_data['Image URL'],
        "attacker_types": attacker_types,
        "level": level_atk,
        "atk_stat_name": atk_stat_name,
        "atk_value": int(atk_stat)
    }
    defender = {
        "defender_name": defender_data['Name'],
        "defender_image_url": defender_data['Image URL'],
        "defender_types": defender_types,
        "def_stat_name": def_stat_name,
        "def_value": int(def_stat)
    }
    move_info = {
        "name" : move_name,
        "attack_type": attack_type,
        "power": base_power
    }
    battle = {
        "stab_mod": stab_mod,
        "type_effectiveness": type_effectiveness,
        "base_calc_no_random": float(base_calc),
        "range_min": int(damage_min),
        "range_max": int(damage_max)
    }

    # Retorna todos os dados formatados para o frontend
    return {
        "attacker": attacker,
        "defender": defender,
        "move_info": move_info,
        "battle": battle
    }

def get_challenge_formula(params, nivel_dificuldade):
    # Gera o dicionário de fórmula e a resposta esperada baseada no nível
    
    # NÍVEL FÁCIL --> focar em STAB e Eficácia
    # Dano = (Poder * 0.5 + 10) * STAB * Eficácia
    if nivel_dificuldade == 'facil':
        base_calc_facil = (params['move_info']['power'] * 0.5) + 10 # Cálculo base simplificado (sem stats e nível)
        answer_facil = np.floor(base_calc_facil * params['battle']['stab_mod'] * params['battle']['type_effectiveness'])

        return {
            "name": "FÁCIL",
            "description": "Foque apenas nos multiplicadores de Poder, STAB e Eficácia de Tipo.",
            "equation_tex": r"\text{Dano} = \lfloor (\frac{\text{Poder}}{2} + 10) \times \text{STAB} \times \text{Eficácia} \rfloor",
            "answer_for_level": int(answer_facil)
        }

    # NÍVEL MÉDIO --> focada no dano exato sem o fator aleatório
    elif nivel_dificuldade == 'medio':
        
        return {
            "name": "MÉDIO",
            "description": "Use a fórmula padrão Pokémon. Lembre-se de seguir a ordem das operações.",
            "equation_tex": r"\text{Dano} = \lfloor \left( \left[ \left( \frac{2 \times \text{Nível}}{5} + 2 \right) \times \frac{\text{Atk}}{\text{Def}} \times \frac{\text{Poder}}{50} \right] + 2 \right) \times \text{STAB} \times \text{Eficácia} \rfloor",
            # params['damage_max'] é o dano exato com fator 1.0
            "answer_for_level": params['battle']['range_max']
        }
    
    # NÍVEL DIFÍCIL --> resultado deve ser a faixa completa de dano (0.85 a 1.0)
    elif nivel_dificuldade == 'dificil':
        
        return {
            "name": "DIFÍCIL",
            "description": "Calcule a Faixa de Dano. Você deve calcular o valor mínimo (Fator 0.85) e o valor máximo (Fator 1.0) e responder Min-Max.",
            "equation_tex": r"\text{Dano} = \lfloor \left( \left[ \left( \frac{2 \times \text{Nível}}{5} + 2 \right) \times \frac{\text{Atk}}{\text{Def}} \times \frac{\text{Poder}}{50} \right] + 2 \right) \times \text{STAB} \times \text{Eficácia} \times \text{Aleatório} \rfloor",
            # A resposta deve ser a string [min-max]
            "answer_for_level": f"[{params['battle']['range_min']} - {params['battle']['range_max']}]",
            "range_min": params['battle']['range_min'],
            "range_max": params['battle']['range_max']
        }
    
    return {}

def calc_xp(group, start, target):
    
    # Função auxiliar - calcula o XP total para nível n
    def xp_at(n):
        match group:
            case "Rápido":
                return (4 * n**3) // 5
                
            case "Médio-Rápido":
                return n**3
                
            case "Médio-Lento":
                # A fórmula é negativa no nível 1, max() para corrigir
                xp = (6 * n**3) // 5 - 15 * n**2 + 100 * n - 140
                return max(0, xp)
                
            case "Lento":
                return (5 * n**3) // 4
                
            case "Errático":
                if n <= 50:
                    return (n**3 * (100 - n)) // 50
                elif n <= 68:
                    return (n**3 * (150 - n)) // 100
                elif n <= 98:
                    return (n**3 * ((1911 - 10 * n) // 3)) // 500
                else:
                    return (n**3 * (160 - n)) // 100
                    
            case "Flutuante":
                if n <= 15:
                    return (n**3 * (((n + 1) // 3) + 24)) // 50
                elif n <= 35:
                    return (n**3 * (n + 14)) // 50
                else:
                    return (n**3 * ((n // 2) + 32)) // 50
            
            case _:
                return -1 # Fallback

    xp_start = xp_at(start)
    xp_target = xp_at(target)

    if xp_start < 0 or xp_target < 0:
        return -1

    # XP total do target menos o que já tem
    answer = xp_target - xp_start
    return answer


def setup_xp(df, nivel):

    # Sorteia o Pokemon de um grupo apropriado para a dificuldade
    if nivel == "facil":
        grupos = ["Lento", "Médio-Rápido", "Rápido"]
    elif nivel == "medio":
        grupos = ["Médio-Lento"]
    elif nivel == "dificil":
        grupos = ["Errático", "Flutuante"]
    else:
        grupos = ["Médio-Lento"]

    candidatos = df[df["Experience Group"].isin(grupos)]
    if candidatos.empty:
        raise ValueError(f"Nenhum Pokémon encontrado para os grupos: {grupos}")
    poke = candidatos.sample(1).reset_index().iloc[0]

    name = poke['Name']
    group = poke['Experience Group']
    current_level = random.randint(5, 81)
    target_level = random.randint(current_level + 1, current_level + 15)

    answer = calc_xp(group, current_level, target_level)

    poke_info = {
        "name": name,
        "growth_group": group,
        "current_level": current_level,
        "target_level": target_level
    }

    return [poke_info, answer]

def get_xp_formula(poke, dificuldade):
    group = poke["growth_group"]
    level_1 = poke["current_level"]
    level_2 = poke["target_level"]

    formulas = {
        "Rápido": ("Crescimento Rápido", r"E(L) = \left\lfloor\frac{4L^3}{5}\right\rfloor"),
        "Médio-Rápido": ("Crescimento Médio-Rápido", r"E(L) = L^3"),
        "Médio-Lento": ("Crescimento Médio-Lento", r"E(L) = \left\lfloor\frac{6L^3}{5}\right\rfloor - 15L^2 + 100L - 140"),
        "Lento": ("Crescimento Lento", r"E(L) = \left\lfloor\frac{5L^3}{4}\right\rfloor"),
        "Errático": ("Crescimento Errático", r"E(L) = \begin{cases}\left\lfloor\frac{L^3(100-L)}{50}\right\rfloor,&L\leq50\\\left\lfloor\frac{L^3(150-L)}{100}\right\rfloor,&51\leq L\leq68\\\left\lfloor\frac{L^3\left\lfloor(1911-10L)/3\right\rfloor}{500}\right\rfloor,&69\leq L\leq98\\\left\lfloor\frac{L^3(160-L)}{100}\right\rfloor,&L\geq99\end{cases}"),
        "Flutuante": ("Crescimento Flutuante", r"E(L) = \begin{cases}\left\lfloor\frac{L^3(\left\lfloor(L+1)/3\right\rfloor+24)}{50}\right\rfloor,&L\leq15\\\left\lfloor\frac{L^3(L+14)}{50}\right\rfloor,&16\leq L\leq35\\\left\lfloor\frac{L^3(\left\lfloor L/2\right\rfloor+32)}{50}\right\rfloor,&L\geq36\end{cases}"),
    }
    name, base_equation = formulas[group]

    return {
        "name": name,
        "description": "Calcule o XP total de cada nível e subtraia: X = E(L2) - E(L1).",
        "equation_tex": rf"{base_equation}\qquad X = E({level_2}) - E({level_1})",
        "difficulty": dificuldade,
    }

def get_captura_formula(is_critical_capture):
    n_shakes = 1 if is_critical_capture else 4

    return {
        "name": "Probabilidade de Captura",
        "description": (
            "Calcule o valor de captura, converta-o na chance de cada movimento "
            f"da Pokébola e eleve o resultado a {n_shakes}."
        ),
        "equation_tex_base": (
            r"a = \left\lfloor\frac{(3 \times \text{HP Max} - 2 \times \text{HP Atual}) "
            r"\times \text{Taxa} \times \text{Modificador da Bola}}"
            r"{3 \times \text{HP Max}} \times \text{Modificador de Status}\right\rfloor"
        ),
        "equation_tex_probability": (
            r"b = \left\lfloor\frac{1048560}{\sqrt[4]{16711680/a}}\right\rfloor"
            rf"\qquad P = \left(\frac{{b}}{{65536}}\right)^{{{n_shakes}}}"
        ),
        "required_shakes": n_shakes
    }

def setup_captura(df, is_lucky):
    # Sorteia um Pokémon para o encontro
    encounter = df.sample(1).reset_index().iloc[0]

    # Informações do Pokémon
    pokemon_name = str(encounter['Name'])
    image_url = str(encounter['Image URL'])
    hp_max = int(encounter['Health'])
    catch_rate = int(encounter['Catch Rate'])

    # Captura Crítica?
    is_critical_capture = False
    n_shakes = 4
    if is_lucky:
        is_critical_capture = True
        n_shakes = 1
    else:
        critical_roll = random.random()
        if critical_roll < 0.05:  # 5% de chance
            is_critical_capture = True
            n_shakes = 1

    # Sorteia a Pokébola
    balls = {
        "Pokébola": {"weight": 60, "modifier": 1.0},
        "Great Ball": {"weight": 30, "modifier": 1.5},
        "Ultra Ball": {"weight": 10, "modifier": 2.0}
    }
    ball_name = random.choices(population=list(balls.keys()), weights=[i["weight"] for i in balls.values()], k=1)[0]
    ball_modifier = balls[ball_name]["modifier"]

    # Sorteia Status
    status_conditions = {
        "Nenhum": {"weight": 6, "modifier": 1.0},
        "Paralisado": {"weight": 3, "modifier": 1.5},
        "Dormindo": {"weight": 2, "modifier": 2.5},
        "Congelado": {"weight": 1, "modifier": 2.5},
        "Envenenado": {"weight": 1, "modifier": 1.5},
        "Queimado": {"weight": 1, "modifier": 1.5}
    }
    status = random.choices(population=list(status_conditions.keys()), weights=[i["weight"] for i in status_conditions.values()], k=1)[0]
    status_modifier = status_conditions[status]["modifier"]

    # Sorteia HP atual
    hp_percentage = random.randint(1, 100)
    hp_current = max(1, hp_percentage * hp_max // 100)

    # Calcula o valor de captura base e a chance final
    base_chance = int((((3 * hp_max - 2 * hp_current) * catch_rate * ball_modifier) / (3 * hp_max)) * status_modifier)

    if base_chance <= 0:
        shake_threshold = 0
        chance = 0.0
    elif base_chance >= 255:
        shake_threshold = 65536
        chance = 1.0
    else:
        shake_threshold = int(1048560 / ((16711680 / base_chance) ** 0.25))
        chance_per_shake = min(shake_threshold / 65536, 1.0)
        chance = chance_per_shake ** n_shakes

    is_captured = random.random() < chance

    # Agrupa Info
    encounter = {
        "pokemon_name": pokemon_name,
        "image_url": image_url,
        "hp_max": hp_max,
        "hp_current": hp_current,
        "catch_rate": catch_rate,
        "status_condition": status,
        "status_modifier": status_modifier
    }
    ball = {
        "name": ball_name,
        "modifier": ball_modifier
    }
    capture = {
        "is_critical_capture": is_critical_capture,
        "required_shakes": n_shakes,
        "is_captured": is_captured,
    }
    answers = {
        "base_chance": base_chance,
        "shake_threshold": shake_threshold,
        "probability_decimal": chance,
        "probability_percentage": f'{chance * 100:.2f}%'
    }

    return [
        encounter,
        ball,
        capture,
        answers
    ]

def binomial_probability(trials, successes, success_probability):
    # Probabilidade de exatamente x sucessos y em trials
    # math.comb calcula combinação de n elementos tomados k a k
    # (Coeficiente Binomial)
    return (
        math.comb(trials, successes)
        * success_probability ** successes
        * (1 - success_probability) ** (trials - successes)
    )

def setup_prob_event(df, moves, dificuldade):

    # Sorteia um golpe impreciso e um Pokémon que aprende esse golpe
    inaccurate_moves = moves[moves["accuracy_below_100"] == True]
    move = inaccurate_moves.sample(1).iloc[0]
    pokemon_indexes = json.loads(move["pokemon_row_indexes"])
    pokemon = df.iloc[random.choice(pokemon_indexes)]

    accuracy_percent = int(float(move["accuracy"]))
    success_probability = round(accuracy_percent / 100, 10)
    failure_probability = round(1 - success_probability, 10)

    pokemon_types = [str(pokemon["Primary Typing"])]
    if pd.notna(pokemon["Secondary Typing"]):
        pokemon_types.append(str(pokemon["Secondary Typing"]))

    pokemon_info = {
        "name": str(pokemon["Name"]),
        "image_url": str(pokemon["Image URL"]),
        "types": pokemon_types,
    }
    move_info = {
        "name": str(move["name"]),
        "type": str(move["type"]),
        "accuracy": accuracy_percent,
        "accuracy_decimal": success_probability,
    }

    if dificuldade == "facil":
        scenario_type = random.choice(["miss_once", "at_least_one_hit"])
        if scenario_type == "miss_once":
            trials = 1
            probability = failure_probability
            description = (
                f"{pokemon_info['name']} usa {move_info['name']}, que possui "
                f"{accuracy_percent}% de precisão. Qual é a chance de errar?"
            )
            formula_description = "Calcule o complemento da chance de acerto."
            equation = r"P(\text{erro}) = 1 - p"
            successes = None
        else:
            trials = random.randint(2, 4)
            probability = 1 - failure_probability ** trials
            description = (
                f"{pokemon_info['name']} usa {move_info['name']} {trials} "
                "vezes. Qual é a chance de acertar pelo menos uma vez?"
            )
            formula_description = (
                "Use o complemento da probabilidade de errar todas as tentativas."
            )
            equation = rf"P(X \geq 1) = 1 - (1-p)^{{{trials}}}"
            successes = None

    elif dificuldade == "medio":
        scenario_type = random.choice(["consecutive_hits", "consecutive_misses", "first_hit_on_attempt", "exactly_k_hits"])
        if scenario_type == "consecutive_hits":
            trials = random.randint(2, 4)
            probability = success_probability ** trials
            description = (
                f"Qual é a chance de {pokemon_info['name']} acertar "
                f"{move_info['name']} {trials} vezes seguidas?"
            )
            formula_description = (
                "Multiplique as probabilidades dos acertos independentes."
            )
            equation = rf"P = p^{{{trials}}}"
            successes = trials
        elif scenario_type == "consecutive_misses":
            trials = random.randint(2, 4)
            probability = failure_probability ** trials
            description = (
                f"Qual é a chance de {pokemon_info['name']} errar "
                f"{move_info['name']} {trials} vezes seguidas?"
            )
            formula_description = (
                "Calcule a chance de erro e multiplique-a em cada tentativa."
            )
            equation = rf"P = (1-p)^{{{trials}}}"
            successes = 0
        elif scenario_type == "first_hit_on_attempt":
            trials = random.randint(2, 5)
            probability = failure_probability ** (trials - 1) * success_probability
            description = (
                f"Qual é a chance de {pokemon_info['name']} acertar "
                f"{move_info['name']} pela primeira vez exatamente na "
                f"{trials}ª tentativa?"
            )
            formula_description = (
                "Multiplique os erros iniciais pelo acerto da tentativa indicada."
            )
            equation = rf"P(T={trials}) = (1-p)^{{{trials - 1}}}p"
            successes = 1
        else:
            trials = random.randint(3, 5)
            successes = random.randint(1, trials - 1)
            probability = binomial_probability(trials, successes, success_probability)
            description = (
                f"Em {trials} usos de {move_info['name']}, qual é a chance "
                f"de {pokemon_info['name']} acertar exatamente {successes}?"
            )
            formula_description = (
                "Use a distribuição binomial e conte as ordens possíveis."
            )
            equation = (
                rf"P(X={successes}) = \binom{{{trials}}}{{{successes}}}"
                rf"p^{{{successes}}}(1-p)^{{{trials - successes}}}"
            )

    else:
        scenario_type = random.choice(["at_least_k_hits", "at_most_k_hits", "between_k_hits"])
        trials = random.randint(5, 8)
        if scenario_type == "at_least_k_hits":
            successes = random.randint(2, trials - 2)
            probability = sum(binomial_probability(trials, k, success_probability) for k in range(successes, trials + 1))
            description = (
                f"Em {trials} usos de {move_info['name']}, qual é a chance "
                f"de {pokemon_info['name']} acertar pelo menos {successes}?"
            )
            formula_description = (
                "Some as probabilidades da quantidade mínima de acertos até o total de tentativas."
            )
            equation = (
                rf"P(X\geq {successes}) = \sum_{{k={successes}}}^{{{trials}}}"
                rf"\binom{{{trials}}}{{k}}p^k(1-p)^{{{trials}-k}}"
            )
        elif scenario_type == "at_most_k_hits":
            successes = random.randint(1, trials - 2)
            probability = sum(binomial_probability(trials, k, success_probability) for k in range(successes + 1))
            description = (
                f"Em {trials} usos de {move_info['name']}, qual é a chance "
                f"de {pokemon_info['name']} acertar no máximo {successes}?"
            )
            formula_description = (
                "Some as probabilidades de zero acertos até a quantidade máxima de acertos indicada."
            )
            equation = (
                rf"P(X\leq {successes}) = \sum_{{k=0}}^{{{successes}}}"
                rf"\binom{{{trials}}}{{k}}p^k(1-p)^{{{trials}-k}}"
            )
        else:
            lower = random.randint(1, trials - 3)
            upper = random.randint(lower + 1, trials - 1)
            successes = {"minimum": lower, "maximum": upper}
            probability = sum(binomial_probability(trials, k, success_probability) for k in range(lower, upper + 1))
            description = (
                f"Em {trials} usos de {move_info['name']}, qual é a chance "
                f"de {pokemon_info['name']} acertar entre {lower} e {upper} "
                "vezes (inclusive)?"
            )
            formula_description = (
                "Some as probabilidades binomiais de todos os valores da faixa."
            )
            equation = (
                rf"P({lower}\leq X\leq {upper}) = "
                rf"\sum_{{k={lower}}}^{{{upper}}}"
                rf"\binom{{{trials}}}{{k}}p^k(1-p)^{{{trials}-k}}"
            )

    scenario = {
        "type": scenario_type,
        "description_text": description,
        "trials": trials,
        "target_successes": successes,
        "events_are_independent": True,
    }
    formula = {
        "name": "Probabilidade de Eventos",
        "description": formula_description,
        "equation_tex": equation,
        "difficulty": dificuldade,
        "variables": {
            "p": round(success_probability, 10),
            "q": round(failure_probability, 10),
            "n": trials,
        },
    }
    answers = {
        "probability_decimal": round(probability, 10),
        "probability_percentage": round(probability * 100, 2),
        "expected_hits": round(trials * success_probability, 10),
        "variance": round(trials * success_probability * failure_probability, 10),
    }
    return {
        "pokemon": pokemon_info,
        "move": move_info,
        "scenario": scenario,
        "formula": formula,
        "answers": answers,
    }

def escolher_ataque_para_pista(ataques, candidatos, tipos_corretos):
    ataques_uteis = []

    for ataque in ataques:
        multiplicador_correto = get_type_effectiveness(ataque, tipos_corretos)
        candidatos_restantes = sum(get_type_effectiveness(ataque, combinacao) == multiplicador_correto for combinacao in candidatos)

        if candidatos_restantes < len(candidatos):
            ataques_uteis.append((ataque, candidatos_restantes))

    ataques_uteis.sort(key=lambda item: item[1])
    tres_melhores = ataques_uteis[:3]

    return random.choice(tres_melhores)[0]


def setup_logic(df, dificuldade):
    tipos = list(TYPE_CHART_DEFENSIVE.keys())
    tipos_ataque = tipos.copy()

    # Monotype para nível fácil
    if dificuldade == "facil":
        pokemon = df[df["Secondary Typing"].isna()].sample(1).iloc[0]
        tipos_corretos = [pokemon["Primary Typing"]]
        candidatos = [[tipo] for tipo in tipos]
        tipos_conhecidos = []
    else:
        # Doubletype para níveis médio e difícil
        pokemon = df[df["Secondary Typing"].notna()].sample(1).iloc[0]
        tipos_corretos = sorted([pokemon["Primary Typing"], pokemon["Secondary Typing"]])
        # Transforma e tupla e normaliza
        # Impede que aconteça algo como Fogo/Voador e Voador/Fogo
        # Isso quebraria a lógica de apenas um resultado
        # Ficaria 0 ou 2, nunca uma única resposta final
        combinacoes = {
            tuple(sorted([linha["Primary Typing"], linha["Secondary Typing"]]))
            for lin, linha in df[df["Secondary Typing"].notna()].iterrows()
        }
        # Volta de tupla para lista
        candidatos = [list(combinacao) for combinacao in combinacoes]

        # Revela um dos tipos na dificuldade média
        # Não revela nenhum tipo na difícil
        tipos_conhecidos = ([random.choice(tipos_corretos)] if dificuldade == "medio" else [])

        # Elimina os candidatos que não compartilham o tipo já conhecido
        # Já que não são mais possíveis, logo não são candidatos
        if tipos_conhecidos:
            candidatos = [
                combinacao for combinacao in candidatos
                if tipos_conhecidos[0] in combinacao
            ]

    # Escolhe pistas que identificam somente a combinação correta
    ataques_disponiveis = tipos_ataque.copy()
    random.shuffle(ataques_disponiveis)
    pistas = []

    while len(candidatos) > 1:
        ataque_escolhido = escolher_ataque_para_pista(ataques_disponiveis, candidatos, tipos_corretos)
        multiplicador = get_type_effectiveness(ataque_escolhido, tipos_corretos)

        candidatos = [
            combinacao for combinacao in candidatos
            if get_type_effectiveness(ataque_escolhido, combinacao)
            == multiplicador
        ]

        ataques_disponiveis.remove(ataque_escolhido)
        pistas.append({"interaction": {0: "não causa dano", 0.25: "pouquíssimo eficaz", 0.5: "pouco eficaz", 1.0: "dano normal", 2.0: "super eficaz", 4.0: "extremamente eficaz"}[multiplicador], "type": ataque_escolhido, "multiplier": multiplicador})

    if dificuldade == "facil":
        descricao = (
            "Use as pistas e a tabela completa para descobrir o tipo defensivo."
        )
    elif dificuldade == "medio":
        descricao = (
            "Um dos tipos já foi revelado. Use as pistas para descobrir o "
            "segundo tipo do Pokémon."
        )
    else:
        descricao = (
            "Use somente as pistas para descobrir os dois tipos do Pokémon."
        )

    return {
        "pokemon": {
            "name": pokemon["Name"],
            "image_url": pokemon["Image URL"],
        },
        "puzzle": {
            "description_text": descricao,
            "clues": pistas,
            "candidate_types": tipos,
            "known_types": tipos_conhecidos,
            "required_selections": len(tipos_corretos) - len(tipos_conhecidos),
        },
        "game_settings": {
            "show_type_chart": True,
            "difficulty": dificuldade,
        },
        "formula": {
            "name": "Tabela de Tipos",
            "description": (
                "Cruze as relações de dano de todas as pistas. O tipo correto "
                "é o único que satisfaz todas elas."
            ),
            "equation_tex": None,
            "difficulty": dificuldade,
        },
        "answers": {
            "correct_types": tipos_corretos,
        },
    }


# -------- Rotas de Navegação --------

@app.route('/')
def pagina_inicial():
    return render_template('pagina_inicial.html')

@app.route('/calculo_dano')
def calculo_dano_page():
    return render_template('minijogos/calculo_dano.html')

@app.route('/calculo_xp')
def calculo_xp_page():
    return render_template('minijogos/calculo_xp.html')

@app.route('/calculo_prob')
def calculo_prob_page():
    return render_template('minijogos/calculo_prob.html')

@app.route('/calculo_prob_event')
def calculo_prob_event_page():
    return render_template('minijogos/calculo_prob_event.html')

@app.route('/calculo_logic')
def calculo_logic_page():
    return render_template('minijogos/calculo_logic.html')

# -------- Rota dos Minigames (API) --------

# Cria os dados da batalha e retorna para o frontend em JSON
@app.route('/api/calculo_batalha', methods=['POST'])
def calculo_batalha():
    data = request.get_json(silent=True) or {}
    nivel_dificuldade = data.get('nivel', 'medio') # Padrão médio se não especificado
    
    if dados_pokemon.empty:
        return jsonify({"erro": "Dados de Pokémon não carregados"})
    if dados_moves.empty:
        return jsonify({"erro": "Dados de ataques não carregados"})
    
    # Configura a batalha
    pokeinfo = setup_battle(dados_pokemon, dados_moves)
    
    # Obtém a fórmula para a dificuldade
    formula = get_challenge_formula(pokeinfo, nivel_dificuldade)
    
    return jsonify({"attacker": pokeinfo["attacker"], "defender": pokeinfo["defender"], "move_info": pokeinfo["move_info"], "battle": pokeinfo["battle"], "formula": formula})

@app.route('/api/calculo_xp', methods=['POST'])
def calculo_xp():
    data = request.get_json(silent=True) or {}
    nivel_dificuldade = data.get('nivel', 'medio')

    if dados_pokemon.empty:
        return jsonify({"erro": "Dados de Pokémon não carregados"})

    pokeinfo = setup_xp(dados_pokemon, nivel_dificuldade)
    
    # Obtém a fórmula para a dificuldade
    formula = get_xp_formula(pokeinfo[0], nivel_dificuldade)

    return jsonify({"pokemon": pokeinfo[0], "formula": formula, "xp": {"answer": pokeinfo[1]}})

@app.route('/api/calculo_captura', methods=['POST'])
def calculo_captura():
    data = request.get_json(silent=True) or {}
    flag_lucky = data.get('is_lucky', False) is True

    if dados_pokemon.empty:
        return jsonify({"erro": "Dados de Pokémon não carregados"})

    pokeinfo = setup_captura(dados_pokemon, flag_lucky)

    # Obtém a fórmula para a dificuldade
    formula = get_captura_formula(pokeinfo[2]["is_critical_capture"])

    return jsonify({"encounter": pokeinfo[0], "ball": pokeinfo[1], "capture": pokeinfo[2], "formula": formula, "answers": pokeinfo[3]})


@app.route('/api/calculo_prob_event', methods=['POST'])
def calculo_prob_event():
    data = request.get_json(silent=True) or {}
    nivel_dificuldade = data.get('nivel', 'medio')

    if dados_pokemon.empty:
        return jsonify({"erro": "Dados de Pokémon não carregados"})
    if dados_moves.empty:
        return jsonify({"erro": "Dados de ataques não carregados"})

    challenge = setup_prob_event(dados_pokemon, dados_moves, nivel_dificuldade)

    return jsonify(challenge)

@app.route('/api/calculo_logic', methods=['POST'])
def calculo_logic():
    data = request.get_json(silent=True) or {}
    nivel_dificuldade = data.get('nivel', 'medio')

    if dados_pokemon.empty:
        return jsonify({"erro": "Dados de Pokémon não carregados"})

    challenge = setup_logic(dados_pokemon, nivel_dificuldade)

    return jsonify(challenge)


# -------- Inicialização do Servidor ---------

if __name__ == '__main__':
    server = Server(app.wsgi_app)
    server.watch('app.py')
    server.watch('templates/*.html')
    server.watch('templates/**/*.html')
    server.watch('static/*.css')
    server.watch('static/imagens/**/*')
    server.serve(port=5000)
