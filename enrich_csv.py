import pandas as pd
import requests
import os

def enriquecer_csv():
    pasta_script = os.path.dirname(os.path.abspath(__file__))
    caminho_csv = os.path.join(pasta_script, 'all_pokemon_data.csv')
    

    df_local = pd.read_csv(caminho_csv)
    dict_experiencia = {}
    
    # A PokéAPI tem 6 IDs de growth-rate
    for i in range(1, 7):
        url = f"https://pokeapi.co/api/v2/growth-rate/{i}/"
        resposta = requests.get(url)
        
        if resposta.status_code == 200:
            dados = resposta.json()
            nome_api = dados['name']
            
            # Traduz os nomes da API para o padrão que conhecemos
            traducao_grupos = {
                'slow': 'Slow',
                'medium': 'Medium Fast',
                'fast': 'Fast',
                'medium-slow': 'Medium Slow',
                'slow-then-very-fast': 'Fluctuating',
                'fast-then-very-slow': 'Erratic'
            }
            nome_formatado = traducao_grupos.get(nome_api, nome_api.title())
            
            # Pega o ID dos Pokémon que pertencem a este grupo
            for pokemon in dados['pokemon_species']:
                # A URL vem no formato: "https://pokeapi.co/api/v2/pokemon-species/25/"
                url_pokemon = pokemon['url']
                dex_id = int(url_pokemon.strip('/').split('/')[-1])
                dict_experiencia[dex_id] = nome_formatado
                

    df_local['National Dex #'] = pd.to_numeric(df_local['National Dex #'], errors='coerce')
    
    # Mapeia a coluna nova com base no Dicionário que montamos
    df_local['Experience Group'] = df_local['National Dex #'].map(dict_experiencia)
    
    df_local.to_csv(caminho_csv, index=False)
    print("Sucesso! A coluna 'Experience Group' foi adicionada.")

if __name__ == "__main__":
    enriquecer_csv()