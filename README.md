# Pokélearn

Aplicação web educacional que usa batalhas, evolução e captura de Pokémon para transformar conteúdos de matemática em desafios interativos.

O projeto foi desenvolvido na disciplina **Projetos em Computação II**, da UNESP, como evolução de um protótipo anterior. O resultado é uma aplicação Flask com cinco minijogos, três níveis de dificuldade, geração procedural de exercícios, fórmulas renderizadas em notação matemática e recursos de apoio como tutoriais, tabela de tipos e calculadora.

> Este é um projeto acadêmico e não oficial. Pokémon e seus elementos visuais pertencem aos respectivos detentores de direitos. O projeto não possui finalidade comercial.

![Logotipo do Pokélearn](static/imagens/logo.png)

## Visão geral

O Pokélearn foi pensado para aproximar conceitos abstratos de um contexto familiar ao estudante. A cada nova rodada, o backend combina dados reais do universo Pokémon com regras matemáticas e devolve ao navegador um desafio, sua fórmula e a resposta esperada.

O frontend apresenta o problema, oferece ferramentas para resolvê-lo e faz a correção imediata. Assim, o estudante não apenas recebe um resultado: ele vê quais variáveis participam do cálculo e como a dificuldade altera o raciocínio exigido.

### O que foi implementado

| Minijogo | Conteúdo trabalhado | Como a dificuldade evolui |
| --- | --- | --- |
| **Cálculo de dano** | Ordem de operações, proporções, multiplicadores e intervalos | Parte de uma fórmula simplificada, passa pelo dano exato e chega à faixa com fator aleatório |
| **Cálculo de experiência** | Funções cúbicas, funções definidas por partes e diferença entre valores | Seleciona grupos de crescimento com fórmulas progressivamente mais complexas |
| **Chance de captura** | Razão, porcentagem, limitadores e modificadores | Combina HP, taxa de captura, Pokébola, condição de estado e captura crítica |
| **Probabilidade de eventos** | Complemento, eventos independentes, distribuição binomial e somatórios | Avança de erro/acerto simples para “pelo menos”, “no máximo” e intervalos de acertos |
| **Lógica dedutiva** | Interseção de restrições e eliminação de hipóteses | Evolui de um tipo com tabela disponível para uma combinação de dois tipos deduzida pelas pistas |

Todos os desafios são gerados no momento da requisição. Pokémon, golpes, níveis, condições e cenários podem variar entre rodadas.

## Demonstração da arquitetura

```text
Navegador
  ├── templates Jinja + HTML/CSS/JavaScript
  ├── KaTeX para fórmulas
  └── tutoriais, calculadora e tabela de tipos
              │ POST /api/...
              ▼
Aplicação Flask (app.py)
  ├── geração aleatória dos desafios
  ├── regras matemáticas e respostas
  ├── regras de dificuldade
  └── serialização das atividades em JSON
              │
              ▼
Camada de dados
  ├── all_pokemon_data.csv (1.184 registros)
  ├── damage_moves.csv (499 golpes filtrados)
  └── type_data.py (matriz de efetividade)
```

A aplicação utiliza uma arquitetura monolítica simples, adequada ao escopo acadêmico: Flask entrega as páginas e expõe as APIs consumidas pelo JavaScript do próprio frontend. Os dados são carregados com Pandas uma vez na inicialização, e cada rota seleciona amostras e calcula um novo exercício.

Mais detalhes estão na [documentação da arquitetura](docs/ARQUITETURA.md).

## Tecnologias

- **Python 3.10+** e **Flask** no backend;
- **Pandas** e **NumPy** para leitura e cálculo sobre os conjuntos de dados;
- **HTML, CSS e JavaScript** no frontend;
- **Jinja** para composição dos templates;
- **KaTeX** para renderização das fórmulas matemáticas;
- **PokeAPI** como fonte usada pelos scripts de enriquecimento de dados;
- **LiveReload** para atualização automática durante o desenvolvimento.

## Como executar localmente

### Pré-requisitos

- Python 3.10 ou superior;
- `pip`;
- conexão com a internet para carregar o KaTeX, as fontes da calculadora e algumas imagens referenciadas pelos dados.

### Instalação

```bash
git clone https://github.com/JoaoBastasini/Pokelearn.git
cd Pokelearn

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python app.py
```

No Windows PowerShell, ative o ambiente com `.venv\Scripts\Activate.ps1`.

Abra [http://127.0.0.1:5000](http://127.0.0.1:5000). O servidor de desenvolvimento observa alterações nos arquivos e recarrega a aplicação automaticamente.

### Verificação rápida da API

Com a aplicação em execução:

```bash
curl -X POST http://127.0.0.1:5000/api/calculo_batalha \
  -H "Content-Type: application/json" \
  -d '{"nivel":"medio"}'
```

Os níveis aceitos pelos minijogos que usam dificuldade são `facil`, `medio` e `dificil`. Quando o campo é omitido, o backend usa `medio`. A rota de captura usa o campo booleano `is_lucky` em vez de um nível.

Consulte a [referência completa das APIs](docs/API.md) e o arquivo com [exemplos integrais de respostas](data/backend_return_example.json).

## Estrutura do repositório

```text
Pokelearn/
├── app.py                         # Aplicação, regras dos jogos e rotas Flask
├── requirements.txt               # Dependências Python fixadas
├── data/
│   ├── all_pokemon_data.csv       # Pokémon, atributos, imagens e golpes
│   ├── damage_moves.csv           # Golpes de dano elegíveis
│   ├── type_data.py               # Tabelas ofensiva e defensiva de tipos
│   └── backend_return_example.json
├── csv_manip/                     # Importação, tradução e normalização dos CSVs
├── templates/
│   ├── cabecalho.html             # Layout e navegação compartilhados
│   └── minijogos/                 # Uma interface para cada atividade
├── static/
│   ├── css/                       # Estilos globais e componentes
│   ├── js/                        # Calculadora, tutorial e tabela de tipos
│   ├── imagens/                   # Identidade e recursos visuais
│   └── tutorial/                  # Imagens finais e arquivos-fonte das instruções
└── docs/                          # Arquitetura, API e pipeline de dados
```

## Dados e reprodutibilidade

Os CSVs processados já fazem parte do repositório, portanto **não é necessário consultar a PokeAPI para executar a aplicação**. A pasta `csv_manip/` registra o processo utilizado para importar, relacionar, traduzir e normalizar esses dados.

O conjunto de golpes exclui movimentos incompatíveis com os exercícios: golpes sem poder numérico, de status, de dano fixo/variável e de múltiplos acertos. Os scripts também relacionam cada golpe aos índices dos Pokémon capazes de aprendê-lo e mantêm um cache de traduções revisadas.

O processo e a responsabilidade de cada script estão descritos em [Pipeline de dados](docs/DADOS.md).

## Decisões de projeto

- **Geração no backend:** evita duplicar regras matemáticas no navegador e entrega ao frontend um contrato JSON consistente.
- **Respostas junto do desafio:** simplifica a correção imediata no protótipo. Em um ambiente competitivo ou avaliativo, a validação deveria ocorrer exclusivamente no servidor.
- **CSV versionado:** permite executar e demonstrar o projeto sem depender da disponibilidade da API de origem.
- **Fórmulas adaptadas:** o objetivo é didático. Algumas mecânicas foram simplificadas e não pretendem reproduzir integralmente todas as gerações dos jogos oficiais.
- **Dificuldade por conceito:** os níveis modificam a estrutura do cálculo ou a quantidade de informações disponíveis, não apenas os números sorteados.

## Estado atual e limitações

O repositório representa um protótipo acadêmico funcional para execução local. Antes de uso em produção, seriam necessários autenticação, persistência de progresso, validação das respostas no servidor, tratamento HTTP de erros mais detalhado, testes automatizados, acessibilidade auditada e uma configuração própria de implantação.

Também não há telemetria nem armazenamento de dados pessoais. Cada desafio existe apenas na resposta enviada ao navegador.

## Autoria

- **João Bastasini:** backend, APIs, regras matemáticas e tratamento dos conjuntos de dados;
- **Caio:** frontend, identidade visual, responsividade, tutoriais e recursos gráficos;
- **Trabalho conjunto:** definição dos contratos, integração, refatoração e testes manuais.

O detalhamento das entregas e da carga horária está em [Descrição das atividades desenvolvidas](DESCRICAO_ATIVIDADES_DESENVOLVIDAS.md).

## Licença e uso de terceiros

Este repositório não declara atualmente uma licença de software. Na ausência de um arquivo `LICENSE`, permanecem reservados os direitos sobre o código produzido pelos autores.

Pokémon é uma marca de seus respectivos proprietários. Dados e imagens usados com finalidade acadêmica podem ter termos próprios nas fontes originais; verifique-os antes de reutilizar ou distribuir o projeto.
