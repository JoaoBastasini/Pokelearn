# Dados e pipeline de preparação

O Pokélearn versiona os conjuntos já processados para que a aplicação possa ser executada sem baixar dados. Esta documentação explica a origem lógica, as transformações e os scripts mantidos em `csv_manip/`.

## Conjuntos consumidos pela aplicação

### `data/all_pokemon_data.csv`

Contém 1.184 linhas e 27 colunas. Entre os campos usados diretamente pelos minijogos estão:

- nome, número da Pokédex, forma e geração;
- tipagem primária e secundária;
- HP, ataque, defesa, ataque especial e defesa especial;
- taxa de captura e grupo de experiência;
- URL da imagem;
- `Damage Move IDs`, um array JSON com IDs de golpes elegíveis.

O arquivo inclui formas alternativas. Por isso, a quantidade de linhas é maior que a quantidade de espécies distintas.

### `data/damage_moves.csv`

Contém 499 golpes. Seus campos registram ID, nome traduzido, tipo, classe física/especial, poder, precisão, PP, prioridade, geração, alvo e dois vínculos auxiliares:

- `accuracy_below_100`: permite selecionar golpes para exercícios de probabilidade;
- `pokemon_row_indexes`: array JSON de índices do CSV principal para Pokémon que aprendem o golpe.

### `data/type_data.py`

Mantém as matrizes ofensiva e defensiva para os 18 tipos. Seus nomes em português são tratados como valores canônicos pelo backend e pelos scripts de tradução.

## Por que os golpes são filtrados

Os exercícios de dano precisam de uma fórmula determinística baseada em poder. Por isso, a importação descarta:

- golpes de status;
- golpes sem poder numérico ou com poder zero;
- golpes de múltiplos acertos;
- movimentos que não podem ser associados a nenhum Pokémon do CSV.

Essa seleção evita apresentar um golpe cuja mecânica especial não seja representada pela fórmula ensinada.

## Scripts

| Script | Responsabilidade | Acesso à rede |
| --- | --- | --- |
| `import_damage_moves.py` | Consulta os golpes da PokeAPI, filtra os elegíveis e cria `damage_moves.csv` | Sim |
| `translate_moves.py` | Traduz nomes, tipos e classes; usa glossário e cache para revisões | Sim, somente para nomes ainda sem cache |
| `normalize_move_names.py` | Padroniza a primeira letra dos nomes de golpes | Não |
| `add_move_ids.py` | Recria `Damage Move IDs` no CSV de Pokémon a partir do vínculo inverso | Não |
| `add_xp_group.py` | Consulta espécies e adiciona seus grupos de crescimento | Sim |
| `translate_types.py` | Normaliza tipos do CSV principal para o padrão do app | Não |
| `translate_xp_groups.py` | Traduz e normaliza os seis grupos de experiência | Não |

Os scripts que sobrescrevem arquivos fazem parte de uma rotina de manutenção, não da inicialização do app. Antes de executá-los, mantenha uma cópia ou use o controle de versão para revisar as alterações.

## Recriação do conjunto de golpes

Com o ambiente virtual ativo e as dependências instaladas:

```bash
python csv_manip/import_damage_moves.py
python csv_manip/translate_moves.py
python csv_manip/normalize_move_names.py
python csv_manip/add_move_ids.py
```

O importador pode realizar muitas requisições e possui retentativas para erros temporários. A tradução mantém `csv_manip/move_name_translations.json` como cache e aplica um glossário manual prioritário a nomes para os quais uma tradução literal perderia o sentido.

Use `--help` nos quatro scripts acima para consultar caminhos alternativos de entrada, saída e cache. Os scripts de tipos e grupos de XP trabalham diretamente no caminho padrão do projeto.

## Ordem de enriquecimento do CSV principal

Se o arquivo-base de Pokémon for substituído, a ordem lógica é:

1. garantir que nomes e `National Dex #` estejam presentes;
2. executar `add_xp_group.py`;
3. normalizar os grupos com `translate_xp_groups.py`;
4. normalizar tipagens com `translate_types.py`;
5. gerar e traduzir `damage_moves.csv`;
6. executar `add_move_ids.py` para atualizar a relação de golpes.

## Integridade esperada

Antes de iniciar a aplicação, os seguintes invariantes devem ser preservados:

- todo tipo de `damage_moves.csv` existe em `TYPE_CHART_OFFENSIVE`;
- `Damage Move IDs` e `pokemon_row_indexes` contêm arrays JSON válidos;
- IDs de golpes referenciados existem em `damage_moves.csv`;
- grupos de experiência usam exatamente: `Rápido`, `Médio-Rápido`, `Médio-Lento`, `Lento`, `Errático` ou `Flutuante`;
- precisão e poder são numéricos nos registros usados pelos respectivos jogos.

O backend valida tipos incompatíveis na inicialização. As demais verificações ainda são garantidas pelo processo de preparação e podem futuramente ser automatizadas em uma suíte de testes de dados.
