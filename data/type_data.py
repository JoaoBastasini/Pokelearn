#Dicionários de tipos

TYPE_CHART_OFFENSIVE = {
    "Normal": {"Pedra": 0.5, "Fantasma": 0, "Metal": 0.5},
    "Fogo": {"Fogo": 0.5, "Água": 0.5, "Grama": 2.0, "Gelo": 2.0, "Inseto": 2.0, "Pedra": 0.5, "Dragão": 0.5, "Metal": 2.0},
    "Água": {"Fogo": 2.0, "Água": 0.5, "Grama": 0.5, "Terra": 2.0, "Pedra": 2.0, "Dragão": 0.5},
    "Grama": {"Fogo": 0.5, "Água": 2.0, "Grama": 0.5, "Venenoso": 0.5, "Terra": 2.0, "Voador": 0.5, "Inseto": 0.5, "Pedra": 2.0, "Dragão": 0.5, "Metal": 0.5},
    "Elétrico": {"Água": 2.0, "Grama": 0.5, "Elétrico": 0.5, "Terra": 0, "Voador": 2.0, "Dragão": 0.5},
    "Gelo": {"Fogo": 0.5, "Água": 0.5, "Grama": 2.0, "Gelo": 0.5, "Terra": 2.0, "Voador": 2.0, "Dragão": 2.0, "Metal": 0.5},
    "Lutador": {"Normal": 2.0, "Voador": 0.5, "Venenoso": 0.5, "Pedra": 2.0, "Inseto": 0.5, "Fantasma": 0, "Metal": 2.0, "Psíquico": 0.5, "Gelo": 2.0, "Sombrio": 2.0, "Fada": 0.5},
    "Venenoso": {"Grama": 2.0, "Venenoso": 0.5, "Terra": 0.5, "Pedra": 0.5, "Fantasma": 0.5, "Metal": 0, "Fada": 2.0},
    "Terra": {"Fogo": 2.0, "Grama": 0.5, "Elétrico": 2.0, "Venenoso": 2.0, "Voador": 0, "Inseto": 0.5, "Pedra": 2.0, "Metal": 2.0},
    "Voador": {"Grama": 2.0, "Elétrico": 0.5, "Lutador": 2.0, "Inseto": 2.0, "Pedra": 0.5, "Metal": 0.5},
    "Psíquico": {"Lutador": 2.0, "Venenoso": 2.0, "Psíquico": 0.5, "Sombrio": 0, "Metal": 0.5},
    "Inseto": {"Fogo": 0.5, "Grama": 2.0, "Lutador": 0.5, "Venenoso": 0.5, "Voador": 0.5, "Psíquico": 2.0, "Fantasma": 0.5, "Sombrio": 2.0, "Metal": 0.5, "Fada": 0.5},
    "Pedra": {"Fogo": 2.0, "Gelo": 2.0, "Lutador": 0.5, "Terra": 0.5, "Voador": 2.0, "Inseto": 2.0, "Metal": 0.5},
    "Fantasma": {"Normal": 0, "Psíquico": 2.0, "Fantasma": 2.0, "Sombrio": 0.5},
    "Dragão": {"Dragão": 2.0, "Metal": 0.5, "Fada": 0},
    "Sombrio": {"Lutador": 0.5, "Psíquico": 2.0, "Fantasma": 2.0, "Sombrio": 0.5, "Fada": 0.5},
    "Metal": {"Fogo": 0.5, "Água": 0.5, "Elétrico": 0.5, "Gelo": 2.0, "Pedra": 2.0, "Metal": 0.5, "Fada": 2.0},
    "Fada": {"Lutador": 2.0, "Venenoso": 0.5, "Metal": 0.5, "Dragão": 2.0, "Sombrio": 2.0}
}

TYPE_CHART_DEFENSIVE ={
    "Normal": {"Lutador": 2.0, "Fantasma": 0},
    "Fogo": {"Fogo": 0.5, "Água": 2.0, "Grama": 0.5, "Terra": 2.0, "Gelo": 0.5, "Inseto": 0.5, "Pedra": 2.0, "Metal": 0.5, "Fada": 0.5},
    "Água": {"Fogo": 0.5, "Água": 0.5, "Grama": 2.0, "Elétrico": 2.0, "Gelo": 0.5, "Metal": 0.5},
    "Grama": {"Fogo": 2.0, "Água": 0.5, "Grama": 0.5, "Gelo": 2.0, "Venenoso": 2.0, "Voador": 2.0, "Inseto": 2.0, "Terra": 0.5, "Elétrico": 0.5},
    "Elétrico": {"Elétrico": 0.5, "Terra": 2.0, "Voador": 0.5, "Metal": 0.5},
    "Gelo": {"Fogo": 2.0, "Lutador": 2.0, "Pedra": 2.0, "Metal": 2.0, "Gelo": 0.5},
    "Lutador": {"Voador": 2.0, "Psíquico": 2.0, "Fada": 2.0, "Inseto": 0.5, "Pedra": 0.5, "Sombrio": 0.5},
    "Venenoso": {"Lutador": 0.5, "Venenoso": 0.5, "Terra": 2.0, "Psíquico": 2.0, "Inseto": 0.5, "Grama": 0.5, "Fada": 0.5},
    "Terra": {"Água": 2.0, "Grama": 2.0, "Gelo": 2.0, "Elétrico": 0, "Venenoso": 0.5, "Pedra": 0.5},
    "Voador": {"Elétrico": 2.0, "Gelo": 2.0, "Pedra": 2.0, "Lutador": 0.5, "Inseto": 0.5, "Grama": 0.5, "Terra": 0},
    "Psíquico": {"Inseto": 2.0, "Fantasma": 2.0, "Sombrio": 2.0, "Lutador": 0.5, "Psíquico": 0.5},
    "Inseto": {"Fogo": 2.0, "Voador": 2.0, "Pedra": 2.0, "Lutador": 0.5, "Terra": 0.5, "Grama": 0.5},
    "Pedra": {"Água": 2.0, "Grama": 2.0, "Lutador": 2.0, "Terra": 2.0, "Metal": 2.0, "Normal": 0.5, "Fogo": 0.5, "Venenoso": 0.5, "Voador": 0.5},
    "Fantasma": {"Fantasma": 2.0, "Sombrio": 2.0, "Normal": 0, "Lutador": 0, "Venenoso": 0.5, "Inseto": 0.5},
    "Dragão": {"Gelo": 2.0, "Dragão": 2.0, "Fada": 2.0, "Fogo": 0.5, "Água": 0.5, "Grama": 0.5, "Elétrico": 0.5},
    "Sombrio": {"Lutador": 2.0, "Inseto": 2.0, "Fada": 2.0, "Fantasma": 0.5, "Sombrio": 0.5, "Psíquico": 0},
    "Metal": {"Fogo": 2.0, "Lutador": 2.0, "Terra": 2.0, "Normal": 0.5, "Voador": 0.5, "Pedra": 0.5, "Inseto": 0.5, "Metal": 0.5, "Grama": 0.5, "Psíquico": 0.5, "Gelo": 0.5, "Dragão": 0.5, "Fada": 0.5, "Venenoso": 0},
    "Fada": {"Venenoso": 2.0, "Metal": 2.0, "Lutador": 0.5, "Inseto": 0.5, "Sombrio": 0.5, "Dragão": 0}
}