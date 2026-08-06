# Arquitetura do Pokélearn

Este documento descreve como a aplicação está organizada, como um desafio percorre o sistema e onde ficam as principais responsabilidades técnicas.

## Componentes

### Aplicação Flask

O arquivo `app.py` concentra quatro responsabilidades:

1. carregar os CSVs na inicialização;
2. implementar as fórmulas e os geradores de desafios;
3. entregar os templates das páginas;
4. expor uma rota JSON para cada minijogo.

Os `DataFrame`s `dados_pokemon` e `dados_moves` ficam em memória durante a execução. Isso elimina leituras de disco a cada rodada e é suficiente para o volume atual de dados.

### Frontend

`templates/cabecalho.html` funciona como layout compartilhado e concentra metadados e navegação. A página inicial e os cinco templates de `templates/minijogos/` estendem esse layout.

Cada tela de minijogo contém a marcação da atividade e o JavaScript responsável por:

- solicitar um desafio com `fetch`;
- preencher Pokémon, golpe, variáveis e fórmula;
- renderizar TeX com KaTeX quando necessário;
- comparar a entrada do estudante com a resposta recebida;
- apresentar o feedback e iniciar uma nova rodada.

Os scripts em `static/js/` implementam recursos reutilizáveis: calculadora flutuante, modal de tutorial e visualização ampliada da tabela de tipos.

### Dados

`data/all_pokemon_data.csv` é a fonte principal de Pokémon. Além dos atributos originais, contém grupo de experiência e IDs de golpes de dano. `data/damage_moves.csv` reúne apenas golpes elegíveis para os desafios e registra os índices dos Pokémon que podem utilizá-los.

`data/type_data.py` é a fonte canônica para os nomes em português e os multiplicadores ofensivos/defensivos. Na inicialização, o backend verifica se todos os tipos do CSV de golpes existem nessa tabela.

## Fluxo de uma rodada

```text
1. Estudante escolhe a dificuldade
              │
2. Frontend envia POST com JSON
              │
3. Rota seleciona dados aleatórios
              │
4. Função aplica regras e fórmula
              │
5. Flask serializa desafio + resposta
              │
6. Frontend renderiza e corrige a entrada
```

Como a seleção usa `random` e `DataFrame.sample`, duas chamadas iguais normalmente retornam atividades diferentes. Não existe estado de sessão ou banco de dados.

## Responsabilidade de cada gerador

### Dano

`setup_battle` seleciona atacante, defensor e um golpe compatível, decide entre atributos físicos e especiais, calcula STAB e efetividade e produz a faixa de dano. `get_challenge_formula` adapta fórmula e resposta à dificuldade.

### Experiência

`setup_xp` seleciona um Pokémon de um grupo de crescimento adequado ao nível e sorteia os níveis inicial e final. `calc_xp` implementa os seis grupos; `get_xp_formula` produz a representação em TeX.

### Captura

`setup_captura` combina HP, taxa de captura, Pokébola, condição de estado e possibilidade de captura crítica. Além da probabilidade calculada, uma nova amostra aleatória determina se a captura simulada ocorreu.

### Eventos

`setup_prob_event` escolhe um golpe com precisão inferior a 100% e um Pokémon que possa aprendê-lo. O nível define a família de cenários: complemento, sequência, primeira ocorrência, valor binomial exato ou soma de uma faixa.

### Lógica

`setup_logic` cria o conjunto inicial de tipagens possíveis. A cada iteração, escolhe uma interação ofensiva que reduz esse conjunto até restar uma única hipótese. No nível médio, um tipo é revelado; no difícil, ambos precisam ser deduzidos.

## Contratos e validação

As APIs aceitam JSON e retornam JSON. O frontend conhece a estrutura das respostas, descrita em [API.md](API.md). A aplicação faz validações de disponibilidade dos datasets, mas ainda não valida estritamente todos os valores de entrada nem atribui códigos HTTP específicos aos erros de dados.

Essa separação permite substituir a interface sem reimplementar as fórmulas. Para evoluir o sistema, o passo natural seria mover geradores, modelos de resposta e rotas para módulos próprios.

## Dependências externas em tempo de execução

- o servidor usa somente arquivos locais e pacotes Python instalados;
- KaTeX é obtido pelo CDN jsDelivr;
- a calculadora referencia fontes do Google Fonts;
- URLs de imagens de Pokémon vêm do CSV e são carregadas pelo navegador.

A PokeAPI não participa da geração cotidiana dos desafios. Ela é consultada apenas quando os scripts de preparação de dados são executados.

## Considerações de produção

O servidor iniciado por `python app.py` utiliza LiveReload e é destinado ao desenvolvimento. Uma implantação real deveria criar uma fábrica de aplicação ou objeto importável por um servidor WSGI, desativar o recarregamento, definir observabilidade, cache de assets, política de CORS quando aplicável e respostas de erro padronizadas.
