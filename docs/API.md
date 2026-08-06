# Referência da API

A API interna do Pokélearn gera atividades para o frontend. Todas as rotas usam `POST`, recebem `Content-Type: application/json` e devolvem JSON.

## Convenções

Para as rotas com dificuldade, o corpo é:

```json
{"nivel": "medio"}
```

Valores usados pela interface: `facil`, `medio` e `dificil`. Se `nivel` for omitido, o padrão é `medio`. O backend atual não rejeita explicitamente valores desconhecidos; clientes devem se limitar aos três valores documentados.

As respostas incluem a solução porque a correção é feita no navegador. Esse contrato é apropriado ao protótipo educacional, mas não deve ser usado para uma avaliação em que a resposta precise permanecer secreta.

## `POST /api/calculo_batalha`

Gera um exercício de dano.

```json
{"nivel": "dificil"}
```

Campos principais da resposta:

| Campo | Conteúdo |
| --- | --- |
| `attacker` | nome, imagem, tipos, nível e atributo ofensivo |
| `defender` | nome, imagem, tipos e atributo defensivo |
| `move_info` | nome, tipo e poder do golpe |
| `battle` | STAB, efetividade, cálculo-base e faixa de dano |
| `formula` | nome do nível, explicação, TeX e resposta esperada |

No nível difícil, `formula.range_min` e `formula.range_max` também são enviados. A resposta textual do intervalo segue o formato `[mínimo - máximo]`.

## `POST /api/calculo_xp`

Gera um exercício de experiência entre dois níveis.

```json
{"nivel": "facil"}
```

`pokemon` identifica o Pokémon, seu grupo de crescimento e os níveis. `formula` contém a função do grupo e sua representação em TeX. `xp.answer` é a diferença entre a experiência acumulada no nível final e no inicial.

As dificuldades selecionam grupos diferentes:

- fácil: Rápido, Médio-Rápido ou Lento;
- médio: Médio-Lento;
- difícil: Errático ou Flutuante, cujas funções são definidas por partes.

## `POST /api/calculo_captura`

Gera uma situação de captura. Esta rota não recebe `nivel`.

```json
{"is_lucky": false}
```

Quando `is_lucky` é literalmente `true`, a rodada força uma captura crítica. Caso contrário, ela ainda pode ocorrer com 5% de chance.

| Campo | Conteúdo |
| --- | --- |
| `encounter` | Pokémon, imagem, HP, taxa de captura e condição de estado |
| `ball` | tipo de Pokébola e multiplicador |
| `capture` | indicadores de captura crítica e sucesso da simulação |
| `formula` | fórmula e escala aplicada |
| `answers` | valor-base e probabilidade em decimal e porcentagem |

`capture.is_captured` é o resultado de uma simulação aleatória baseada na probabilidade calculada; ele não altera a resposta matemática esperada.

## `POST /api/calculo_prob_event`

Gera um problema baseado na precisão de um golpe.

```json
{"nivel": "medio"}
```

`scenario.type` identifica a família sorteada. Os cenários possíveis são:

| Dificuldade | Cenários |
| --- | --- |
| Fácil | `miss_once`, `at_least_one_hit` |
| Médio | `consecutive_hits`, `consecutive_misses`, `first_hit_on_attempt`, `exactly_k_hits` |
| Difícil | `at_least_k_hits`, `at_most_k_hits`, `between_k_hits` |

A resposta inclui Pokémon, golpe, enunciado, quantidade de tentativas, fórmula, variáveis `p`, `q` e `n`, probabilidade correta, esperança e variância.

## `POST /api/calculo_logic`

Gera um problema de dedução de tipagem por efetividade.

```json
{"nivel": "dificil"}
```

`puzzle.clues` lista tipos de ataques, descrições da interação e multiplicadores. `candidate_types` contém os tipos selecionáveis; `known_types` traz os já revelados; `required_selections` informa quantos faltam. A solução está em `answers.correct_types`.

- fácil: Pokémon de um tipo;
- médio: Pokémon de dois tipos, com um revelado;
- difícil: Pokémon de dois tipos, sem revelação inicial.

## Erros atuais

Se um dataset essencial não for carregado, a rota retorna um objeto como:

```json
{"erro": "Dados de Pokémon não carregados"}
```

Na implementação atual, esse caso não define um status HTTP de erro e, portanto, responde com `200`. Uma evolução recomendada é usar códigos `4xx` para entradas inválidas, `5xx` para falhas de inicialização e um esquema uniforme de erros.

Exemplos completos, incluindo todos os campos condicionais, estão em [`data/backend_return_example.json`](../data/backend_return_example.json).
