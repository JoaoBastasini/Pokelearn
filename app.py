from flask import Flask, render_template, request, jsonify
from livereload import Server
import pandas as pd
import numpy as np
import random
import os
from type_data import TYPE_CHART_OFFENSIVE, TYPE_CHART_DEFENSIVE

'''
Para rodar o servidor Flask:
1. Certifique-se de que você tem o Flask e o Pandas instalados: pip install Flask pandas
2. Execute este arquivo: python app.py
3. Acesse no navegador: http://127.0.0.1:5000/
'''

app = Flask(__name__)

# -------- Carregar Dados --------

# Carrega os dados do .csv de forma relativa tanto ao diretório atual quanto ao sistema operacional
# os.path.dirname(__file__) pega o diretório
# os.path.join monta o caminho corretamente independentemente do SO
try:
    caminho_csv = os.path.join(os.path.dirname(__file__), 'all_pokemon_data.csv')
    dados_pokemon = pd.read_csv(caminho_csv)
    print("Dados de Pokémon carregados com sucesso.")
except FileNotFoundError:
    print("ERRO: O arquivo all_pokemon_data.csv não foi encontrado. Verifique o caminho.")
    dados_pokemon = pd.DataFrame() # Cria um DataFrame vazio para evitar erros


# -------- Funções Lógicas dos Minigames --------

# Calcula o multiplicador de eficácia do tipo
def get_type_effectiveness(attack_type, defender_types):
    multiplier = 1.0
    for d_type in defender_types:
        # Primeiro .get retorna o dicionário do tipo de ataque
        # Segundo .get retorna o valor de eficácia contra o tipo defensor, no caso de dual type, entra nesse trecho duas vezes (for)
        # Se não tem nada no dicionário, o ataque é neutro, multiplicador 1.
        effectiveness = TYPE_CHART_OFFENSIVE.get(attack_type, {}).get(d_type, 1.0)
        multiplier *= effectiveness
    return multiplier

# Escolhe aleatoriamente o atacante, defensor, níveis e ataque.
def setup_battle(df):    
    
    # Escolhe os Pokémon
    # Faz um DF com um único elemento, aleatório
    # Reseta o índice, o original vira uma coluna chamada 'index' e o novo é 0.
    # Seleciona o primeiro e único elemento com iloc[0]
    attacker_data = df.sample(1).reset_index().iloc[0]
    defender_data = df.sample(1).reset_index().iloc[0]
    
    # Sorteia os níveis dos Pokémon
    level_atk = random.randint(40, 60) # Níveis em uma faixa razoável

    # Garante que o nível do defensor fique entre 40 e 60 e a diferença seja no máximo 10
    # level_def = random.randint(max(40, level_atk - 10), min(60, level_atk + 10))
    # Aparentemente o nível do defensor não é usado no cálculo de dano, então foi comentado, mas caso venha a calhar, está aí.

    # Escolhe o poder do ataque (múltiplo de 10 de 40 a 120)
    base_power = random.choice(range(40, 121, 10))

    # Determina se é físico ou especial, por sorteio, e seleciona os stats correspondentes
    is_physical = random.choice([True, False])

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
    all_types = list(TYPE_CHART_OFFENSIVE.keys())

    attacker_types = [] # Lista vazia para armazenar os tipos válidos
    attacker_types.append(attacker_data['Primary Typing']) # Armazena o primeiro
    if pd.notna(attacker_data['Secondary Typing']):
        attacker_types.append(attacker_data['Secondary Typing']) # Armazena o segundo, se houver
    
    # 50% de chance de ser STAB (mesmo tipo, com bônus de 1.5 no dano), 50% de chance de ser outro tipo
    if random.random() < 0.5 and attacker_types:
        attack_type = random.choice(attacker_types)
    else:
        # Escolhe um tipo que não seja do atacante
        non_stab_types = []
        for t in all_types:
            if t not in attacker_types:
                non_stab_types.append(t)
        attack_type = random.choice(non_stab_types)

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

    # Retorna todos os dados formatados para o frontend
    return {
        "attacker_name": attacker_data['Name'],
        "attacker_image_url": attacker_data['Image URL'],
        "defender_name": defender_data['Name'],
        "defender_image_url": defender_data['Image URL'],
        "attacker_types": attacker_types,
        "defender_types": defender_types,
        "level": level_atk,
        "power": base_power,
        "atk_stat_name": atk_stat_name,
        "def_stat_name": def_stat_name,
        "atk_value": int(atk_stat),
        "def_value": int(def_stat),
        "attack_type": attack_type,
        "stab_mod": stab_mod,
        "type_effectiveness": type_effectiveness,
        "base_calc_no_random": base_calc,
        "range_min": int(damage_min),
        "range_max": int(damage_max)
    }

def get_challenge_formula(params, nivel_dificuldade):
    # Gera o dicionário de fórmula e a resposta esperada baseada no nível
    
    # NÍVEL FÁCIL --> focar em STAB e Eficácia.
    # Dano = (Poder * 0.5 + 10) * STAB * Eficácia
    if nivel_dificuldade == 'facil':
        base_calc_facil = (params['power'] * 0.5) + 10 # Cálculo base simplificado (sem stats e nível)
        answer_facil = np.floor(base_calc_facil * params['stab_mod'] * params['type_effectiveness'])
        
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
            "answer_for_level": params['range_max']
        }
    
    # NÍVEL DIFÍCIL --> resultado deve ser a faixa completa de dano (0.85 a 1.0)
    elif nivel_dificuldade == 'dificil':
        
        return {
            "name": "DIFÍCIL",
            "description": "Calcule a Faixa de Dano. Você deve calcular o valor mínimo (Fator 0.85) e o valor máximo (Fator 1.0) e responder Min-Max.",
            "equation_tex": r"\text{Dano} = \lfloor \left( \left[ \left( \frac{2 \times \text{Nível}}{5} + 2 \right) \times \frac{\text{Atk}}{\text{Def}} \times \frac{\text{Poder}}{50} \right] + 2 \right) \times \text{STAB} \times \text{Eficácia} \times \text{Aleatório} \rfloor",
            # A resposta deve ser a string [min-max]
            "answer_for_level": f"[{params['range_min']} - {params['range_max']}]",
            "range_min": params['range_min'],
            "range_max": params['range_max']
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
                elif n <= 36:
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
    data = request.get_json()
    nivel_dificuldade = data.get('nivel', 'medio') # Padrão médio se não especificado
    
    if dados_pokemon.empty:
        return jsonify({"erro": "Dados de Pokémon não carregados"})
    
    # Configura a batalha
    params = setup_battle(dados_pokemon)
    
    # Obtém a fórmula para a dificuldade
    formula = get_challenge_formula(params, nivel_dificuldade)
    
    return jsonify({
        "battle": params,
        "formula": formula
    })

@app.route('/api/calculo_xp', methods=['POST'])
def calculo_xp():
    data = request.get_json(silent=True) or {}
    nivel_dificuldade = data.get('nivel', 'medio')

    if dados_pokemon.empty:
        return jsonify({"erro": "Dados de Pokémon não carregados"})

    pokeinfo = setup_xp(dados_pokemon, nivel_dificuldade)
    
    # Obtém a fórmula para a dificuldade
    formula = get_xp_formula(pokeinfo[0], nivel_dificuldade)

    return jsonify({
        "pokemon": pokeinfo[0],
        "formula": formula,
        "xp": {"answer": pokeinfo[1]}
    })


# -------- Inicialização do Servidor ---------

if __name__ == '__main__':
    server = Server(app.wsgi_app)
    server.watch('app.py')
    server.watch('templates/*.html')
    server.watch('templates/**/*.html')
    server.watch('static/*.css')
    server.watch('static/imagens/**/*')
    server.serve(port=5000)
