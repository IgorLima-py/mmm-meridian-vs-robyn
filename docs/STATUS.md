# Status

_Atualizado: 2026-09-29 (C12, na Karen)_

## Sessão C12 (29/09, Karen): o que os alocadores das próprias ferramentas recomendam

bateria 7: 60/0/0 (`python -m simulation.checks`, 29/09, antes do push)

### O que foi feito

Sem refit: os modelos salvos em `outputs/` (só na Karen) foram reaproveitados.

- **`runs/robyn/run_robyn_allocator.R`**: `robyn_allocator()` sobre o `OutputCollect.rds` e o
  modelo escolhido pela regra pré-registrada (`extras.selected_model`). `InputCollect` não foi
  salvo pelo `run_robyn.R`; é refeito pelo mesmo `robyn_inputs()`, e o script para se o gasto da
  janela refeito não bater com o do modelo salvo. Limites 0,5 e 2,0 (também os defaults do
  alocador, lidos da fonte). Segundos por seed.
- **`runs/meridian/run_meridian_allocator.py`**: `BudgetOptimizer.optimize()` no posterior,
  `spend_constraint_lower=0.5`, `spend_constraint_upper=1.0` (o Meridian declara os limites
  relativos ao gasto histórico), orçamento fixo, resto default. 441 s na primeira seed (XLA
  frio), 69 a 84 s nas outras.
- **10 JSONs** `runs/{meridian,robyn}/results/*_national_allocation_seed10?.json`; entradas
  datadas em `runs/*/DECISIONS.md` (a do Robyn diz 101-104 em 4000×5, 105 em 2000×5, e que 102,
  103 e 104 não convergiram pelo teste do próprio Robyn).
- **`analysis/validate_schema.py`**: `BUDGET_RTOL` de 1e-6 para 2e-3, com a origem medida no
  comentário; nota no `RESULTS_SCHEMA.md`. `analysis/out/summary.md` ganhou as duas linhas
  "own allocator".

### Resultado, em poucas linhas (leitura para a C13, não texto publicado)

Limites [0,5; 2,0], média sobre as 5 seeds, regret / uplift capturado:

- Alocador do Meridian: 6,6% (2,6 a 9,9%) / −0,12. Alocador do Robyn: 15,5% (0,9 a 21,7%) /
  −1,59. "Não realocar" perde 6,0%.
- As mesmas curvas estimadas dão 5,6% (Meridian) e 5,9% (Robyn) no otimizador neutro da C11.
  Ou seja, o alocador próprio piorou o resultado nas duas ferramentas, e muito mais no Robyn.
  Esta sessão não separou por quê (curva do alocador diferente da exportada, ótimo local do
  SLSQP, ou outra coisa): não afirmar causa na C13.
- Os planos do Robyn batem nos limites (muitos canais em 0,5 ou 2,0).

### O que foi tentado e falhou — não repita

- **Primeira rodada do Meridian usou como base o `nonoptimized_data` do próprio Meridian**: ele
  arredonda o orçamento para a grade (120,1 M ou 120,0 M contra 120,12 M observados) e monta
  essa tabela com o orçamento arredondado; os multiplicadores saíam contra a base errada e o
  validador reprovou o orçamento. Refeito com o gasto observado de `mmm.input_data`.
- **Nomes de canal do `dt_optimOut` do Robyn são os de exposição (`tv_I`)**, não os de gasto:
  a primeira tentativa falhou nisso (é o F7 de novo).

### Números sem medição

O `BUDGET_RTOL` agora é medido (maior lacuna 9,99e-4, Meridian). O Meridian ficou entre 1,7e-4 e
1e-3 abaixo do orçamento; o efeito dessa sub-execução no regret não foi separado e é ordem de
1% do uplift possível. A C13 deve citar isso se citar o número.

### Segunda opinião (Opus, no /tchau)

Sem achado. Conferiu o `sai:` e o `verificar:`, a base do multiplicador, a tolerância nova, a
leitura do Robyn, as duas entradas de `DECISIONS.md` e que não entrou dependência.

### Preso a esta máquina (Karen)

Os modelos em `outputs/meridian/*.pkl` e `outputs/robyn/seed*/`. Os 10 JSONs viajam pelo git,
então a C13 não precisa da Karen.

### Próximo passo

C13 — parte 2 escrita (`article/part-2.md`, figuras, `docs/drafts/README-part2.md`). Qualquer
máquina. Leia o **entra** da C13 no `docs/ROADMAP.md`.

## Sessão C11 (29/09, Karen): o erro custa dinheiro? Regret de orçamento

bateria 6: 5/0/0 (`python -m simulation.checks`, 29/09, antes do push; 5 seeds OK, avisos
C7 de ooh/display abaixo do piso, como sempre)

### O que foi feito

Nenhuma ferramenta rodou; tudo sobre as curvas que os extratos da v1 já trazem.

- **`analysis/regret.py`** (`cb72543`): otimizador neutro e exato por enumeração de vértices
  (objetivo separável e linear por partes na grade do gerador, uma restrição de orçamento,
  caixa por canal: o ótimo tem no máximo um canal fora de breakpoint). `BOUNDS` com as duas
  faixas do PLAN §8.5 e a origem de cada uma comentada. `--selftest` com quatro testes: curvas
  verdadeiras dão regret 0; caso de dois canais feito à mão dá 3/11 (e uplift −1/2); 200 mil
  planos aleatórios viáveis por seed × limite × canal livre não batem o ótimo; arquivo de
  alocação no ótimo dá 0. Já lê os arquivos de alocação da C12 (`"kind": "allocation"`) e
  gera a linha "`<Tool>` own allocator" na tabela sem mudança de código.
- **`analysis/validate_schema.py`** (`cb72543`): erro = o que o scorer pularia ou leria errado
  em silêncio (canal com outro nome ou ausente, `roi.point` ausente, curva fora da grade,
  NaN, intervalo com uma ponta só, schema ≠ 1.x, seed sem ground truth); aviso = fora da letra
  do schema mas inofensivo hoje (chave desconhecida, nome de arquivo fora da convenção).
  `--strict` reprova os dois. `--allocations` confere limites contra o `BOUNDS` e o orçamento.
  Padrão de glob que não acha nada sai 2. Expande glob por conta própria (o PowerShell não
  expande). Testado contra sete arquivos quebrados de propósito e duas alocações, no scratchpad.
- **`analysis/RESULTS_SCHEMA.md`**: documenta o `ols_ci90` (os oráculos usam desde a v1 e não
  estava escrito), o formato do arquivo de alocação que a C12 vai gravar
  (`<tool>_<arm>_allocation_seed<NNN>.json`, só `multiplier` por canal, `bounds` = nome no
  `BOUNDS`) e o validador.
- **`analysis/scoring.py`**: anexa a tabela `## Budget regret` ao summary, grava
  `analysis/out/regret_long.csv` (ignorado pelo git, como o `metrics_long.csv`), e deixa os
  arquivos de alocação para o `regret.py`.
- **`analysis/out/summary.md`** (`bf9c966`): só ganhou a seção nova; o resto não mudou.

### Resultado, em poucas linhas (leitura para a C13, não texto publicado)

Limites [0,5; 2,0], média sobre as seeds:

- A melhor realocação rende só ~6,5% sobre a alocação observada (6,0–6,5% por seed).
  "Não realocar" perde 6,0% do possível; isso é a régua.
- Meridian nacional perde 5,6%, Robyn 5,9% (0,5% a 13%): quase a régua. Uplift capturado
  médio 6% e 1%; com seeds abaixo de zero (pior que não mexer), Robyn até −121% na 103, onde
  dobra o ooh (canal abaixo do piso).
- Oráculos: L2 0,7%, L3 2,2%, L6 2,3%, L7 2,5%. **Os limites de setup custam quase nada em
  dinheiro**; o que separa as ferramentas dos oráculos é o "resto", como na decomposição da C10.
- Todo ótimo é vértice único: nenhum plano foi escolhido por empate.

**Decisão minha, sem consulta:** a linha de referência "keep the observed allocation" na tabela
não estava no pré-registro; está marcada assim no próprio summary. Se o Igor não quiser, sai
em uma edição no `regret.summary_lines`.

### O que foi tentado e falhou — não repita

- **Substituição com `\n` via heredoc Python no Bash** virou quebra de linha real e quebrou a
  sintaxe do `scoring.py`, duas vezes; o Edit resolveu. Para string com escape, usar o Edit.
- **Rodar o `oracle.py` na Karen regrava os 10 JSONs de L6/L7 com CRLF** (conteúdo idêntico,
  `git diff --ignore-cr-at-eol` vazio). Restaurei com `git checkout -- runs/oracle/results/`.
  Não é regressão, mas vai aparecer como `M` no status sempre que a cadeia rodar aqui.

### Números sem medição (declarados no código)

As tolerâncias do validador para alocação (limite 1e-9, orçamento 1e-6 relativo) e do empate
no otimizador (1e-9) estão na escala do ruído de ponto flutuante, não medidas. **A C12 mede a
folga real de orçamento que cada alocador reporta** e emenda o `BUDGET_RTOL` com a origem se
precisar.

### Segunda opinião (Opus, no /tchau)

A primeira tentativa morreu no limite de uso da API; a segunda rodou. Sem achado que bloqueie
o `sai:`/`verificar:`: refez o caso à mão (3/11, −1/2), confirmou a enumeração de vértices
contra o §8.5 (vale para curva em S), a escala das curvas (inclusive Meridian geo) e que o
validador cobre todo pulo silencioso do `score_result`. Nenhuma dependência nova. Um achado
menor, **corrigido antes do push** (`a437f4e`): resultado sem `response_curve` de estimador
listado derrubaria o `scoring.py` inteiro; agora sai da tabela com o nome ao lado.

### Preso a esta máquina (Karen)

Nada novo desta sessão. Para a C12 (só na Karen): os modelos salvos em `outputs/meridian/*.pkl`
e `outputs/robyn/seed*/OutputCollect.rds`.

### Próximo passo

C12 — rodar `robyn_allocator()` e o `BudgetOptimizer` do Meridian sobre os modelos salvos, sem
refit, com `regret.BOUNDS["primary"]`, e gravar 10 JSONs de alocação no formato do
`RESULTS_SCHEMA.md` (seção "Allocation files"). Validar com
`python analysis/validate_schema.py --strict --allocations runs/*/results/*allocation*.json`;
a cadeia do /score já põe as linhas "own allocator" na tabela. Máquina: Karen.

## Sessão C10 (29/09, Karen): quanto do erro da v1 era setup

bateria 5: 5/0/0 (`python -m simulation.checks`, 29/09, antes do push)

### O que foi feito

Nenhuma ferramenta rodou; tudo é camada de análise sobre os dados e os extratos da v1.

- **Pré-registro da parte 2** em `docs/PLAN.md` §8, commit só dele (`65c0527`), antes de
  qualquer número: degraus L5–L7, projeções sem ruído, as definições das três perguntas do
  AUDIT, a decomposição, rank agreement, dispersão por seed, e regret com limites por canal
  para a C11/C12. **Limites escolhidos por mim, sem consulta:** primário [0,5; 2,0] por canal
  (padrão `max_response` do `robyn_allocator` 3.12.1), sensibilidade [0,7; 1,3] (padrão de
  orçamento fixo do `BudgetOptimizer` do Meridian 1.8.0). Os dois foram lidos do código
  instalado na WSL da Karen, não de doc. O Igor pode vetar por emenda antes da C11.
- **Duas emendas no mesmo dia** (§8.6 `7a5c795`, §8.7 `e01b5c0`), explicadas abaixo em "o que
  falhou". O resultado: L5 aposentado; L6 `oracle_nat_meridian_setup` e L7
  `oracle_nat_robyn_setup` são L3 com o regressor de cada canal trocado pela melhor
  aproximação da curva verdadeira dentro do espaço de parâmetros de cada ferramenta.
- **Código** (`01b680c`): `analysis/oracle.py` (projeções, check, `--diagnostics` com Q1–Q3),
  `analysis/scoring.py` (rank agreement, Meridian − Robyn seed a seed, tabela de decomposição
  pré-registrada e, ao lado, uma versão com sinal marcada como não pré-registrada). 10 JSONs
  novos em `runs/oracle/results/`; os 20 antigos não mudaram de conteúdo.
- **Texto** (`f93ad91`): seção `## Setup-constrained rungs` no fim do `analysis/ORACLE.md`
  (o resto da página é o registro da v1, intocado); `docs/BACKLOG.md` item 8 aponta para ela.
  **Não passou pela `humanize`** — fica para a C13/C14, quando vai a público.

### Resultado, em uma linha por pergunta

- **Q1:** o espaço do Meridian (slope 1, e na tv o k no teto do `ec_m`) empurra a tv para
  **cima** (+0,24 sem ruído); o Meridian errou para **baixo** (−0,34). Não explica nada da tv; em search e social explica ~1/6 e ~1/9.
- **Q2:** o teto de θ do Robyn em ooh/display não chega à tv (0,000). O espaço do Meridian
  só na tv mexe ooh em −0,04 sem ruído; com ruído +0,21 em média, mas troca de sinal entre
  seeds (ooh está abaixo do piso).
- **Q3:** os limites de γ do Robyn contêm o k verdadeiro nos 25 canal-seed (γ 0,36–0,67).
- **Decomposição:** em tv, search e social, os limites do Robyn custam ~0 e o do Meridian
  pouco; o erro das duas está no "resto" (estimar a forma + priors + máquina da ferramenta).
- **Meridian − Robyn por seed:** média −0,022, dp 0,226 — sem vencedor com 5 seeds.

### O que foi tentado e falhou — não repita

- **Ajuste conjunto da forma (L5, §8.1).** Descida por coordenadas no grid, canal a canal,
  8 partidas. O check pré-registrado (achar a verdade sem ruído a partir das 7 partidas
  aleatórias) falhou nas 5 seeds: erro máx de ROI 0,67 a 5,8 (`a9e062b`,
  `python analysis/oracle.py --rungs L5`). Não é bug: na verdade o SSR é ~1e-16, e as
  partidas param em formas com SSR ~1e-7 do total. Um teste exploratório com 40 partidas
  (script não guardado) achou a verdade em 0 de 40 nas seeds 101–103. No agregado nacional
  as 5 formas são quase não-identificadas juntas, mesmo sem ruído. Mais partidas não
  resolvem; um otimizador contínuo talvez, mas não foi tentado (scipy não está no lock).
- **Grade de k até 4,00.** A projeção da tv no espaço do Meridian parou no teto da grade, não
  no do Meridian (o `ec_m` ≤ 10 mapeia para k ≈ 5,3 na tv). Grade ampliada para 10,00 (§8.7),
  e o `oracle.py` agora aborta se o teto do `ec_m` passar da grade. Os dois agregados vistos
  antes da emenda (L6 0,661, L7 0,635) estão declarados nela.
- **Heredoc com apóstrofo no Bash** falhou uma vez ao anexar texto no PLAN; o Edit resolveu.

### Segunda opinião (Opus, no /tchau)

Sem achado que bloqueie o `sai:`/`verificar:`. Dois achados menores de texto, corrigidos
no `ORACLE.md` antes do push: o desvio da tv vem do slope 1 **e** do teto do `ec_m`, não do
slope sozinho; e a faixa dos ROIs do Robyn é 1,02x–1,32x por seed (1,08x era a das médias).
Terceiro, só informativo: o Meridian com `max_lag=13` usa 14 pesos e o L6 usa 13, como o
PLAN §8.1 já declarava.

### Preso a esta máquina (Karen)

Nada novo. As constantes das ferramentas (priors do Meridian, `saturation_hill` e defaults do
alocador do Robyn) foram lidas dos pacotes da WSL e estão citadas no PLAN §8; o Dell não
precisa delas para rodar nada da C10.

### Próximo passo

C11 — regret de orçamento com otimizador neutro, pelo pré-registro do `docs/PLAN.md` §8.5
(com L5 fora da lista de estimadores, §8.6). Máquina: qualquer.

## Sessão /360 da v2 (27–29/09, Karen): avaliação da v1 e o roadmap das partes 2 e 3

Não foi fatia: foi um `/360`, aberto com o ponteiro ainda na C8. Nenhum código mudou.

### O que foi feito

- **A v1 está pública e fechada.** O GitHub detecta a licença MIT (commit `6708dbf`) e o
  Igor aplicou o About. O `verificar:` da C8 já estava satisfeito pela seção de 24/09:
  `LICENSE` na raiz, o README nomeia a licença e o clone limpo roda as seis chamadas. O
  ponteiro só não tinha avançado.
- **O `/360`:** avaliação honesta da v1 (abaixo), uma entrevista a fundo em 7 rodadas,
  três conferentes nos `verificar:` (17 itens ganharam critério que dá para checar) e um
  refutador em Opus, cujos 11 achados foram todos corrigidos antes da aprovação.
- **Arquivos** (commit `035ef85`):
  - `docs/ROADMAP.md` novo, no template do playbook: perfis (com `publicacao`, opus/xhigh),
    a fila C10–C23, uma seção por fatia, a tabela de escape e as decisões da entrevista.
  - `docs/ROADMAP_V1.md`, que é o roadmap antigo sem mudança e guarda a spec da C7.
  - `docs/PROXIMO.md` apontando para a C10.
  - No `CLAUDE.md`: a linha `stack travada:`, "já é público", e o `/oi` e o `/tchau` lendo
    os blocos novos.
- **O hook de abertura voltou a conferir o perfil:** rodei-o contra os arquivos novos e
  ele deu `perfil x tabela: BATE (dificil = opus/high)`. Com o roadmap antigo, ele dizia
  "nao achei a secao Tabela de perfis".

### Avaliação da v1 (/360 de 27/09)

A C17 lê isto antes de pré-registrar a parte 3.

**O que é bom de verdade:**
- A verdade é conhecida e existe o oráculo, que separa "a ferramenta falhou" de "o dado
  não deixava".
- Não achei benchmark publicado que traga o Robyn junto, nem um que pontue a decisão de
  orçamento.
- Tem pré-registro com emendas datadas, auditoria pública e limitações específicas.
- O conselho "rode uma checagem de recuperabilidade antes" é útil e original. É ele que
  vira a C15.

**O que é fraco:**
1. O resultado principal é um empate entre dois setups com deficiência, não entre duas
   ferramentas: o slope do Meridian fica fixo em 1 em 4 canais, e os bounds do Robyn
   excluem o adstock verdadeiro de ooh e display. A C10 ataca isso.
2. O Robyn é frágil: 3 de 5 seeds não convergem, e a média mistura duas specs. O braço geo
   tem 2 seeds, uma sem convergir, então é anedota.
3. Cinco seeds e nenhuma incerteza sobre a diferença entre as ferramentas: 0,533 contra
   0,555 é ruído.
4. O regime é o fácil: gasto exógeno, efeito constante, família funcional certa e ruído iid.
5. O desenho não foi feito para o que acabou medindo. O S/N da tv é 1,9, contra no máximo
   0,4 nos outros canais, e isso só apareceu depois dos runs.
6. Falta a métrica de decisão, o regret de orçamento, e as curvas para calculá-la já estão
   nos extratos. É a C11.
7. A v1 envelheceu:
   - o Meridian 2.0 saiu em 02/09 e o 2.1 em 17/09;
   - o mmm-recovery-bench apareceu em 24/09;
   - o benchmark do Heusch saiu no arXiv 2608.21130.
8. O artigo tem ~1.800 palavras, com ressalva em quase toda frase, e o conselho útil só
   aparece no fim.

**Os dados fazem sentido?** Sim, para o que se propõem:
- O processo gerador é o de Jin et al. 2017, com ROIs entre 0,8 e 3,5.
- Pela config, a mídia responde por ~25% da receita (Σ ROI × gasto ≈ 1,64 M por semana,
  sobre uma base de 5 M).
- O ponto menos realista é o search exógeno com ROI 3,5, que é justamente o que o cenário
  endógeno da parte 3 ataca.

**Projetos irmãos:**
- **experiment-calculators** (público): a calculadora de geo-holdout dimensiona o
  experimento da parte 3, via link.
- **O projeto de geo-holdout, ainda privado:** conecta só pelo método, e entra como
  citação depois de publicado.

### O que foi tentado e falhou

- **`Write` negado dentro do `/360`:** o comando bloqueia a escrita até a mensagem seguinte
  do Igor. O plano ficou no contexto e foi escrito depois do "Tentar novamente".
- **O classificador do modo automático não deu veredito, duas vezes**, no primeiro comando
  da implementação, um `pull + mv + exclude` encadeado. Era transitório: os mesmos passos,
  como comandos separados, passaram.
- **Um `/batch` sem argumento foi chamado no fim da sessão.** Foi erro de digitação do
  Igor, e nada rodou.

### Preso a esta máquina (Karen)

- **`.git/info/exclude`** tem `.agents/`, `.codex/` e `AGENTS.md`, os espelhos do Codex.
  Isso não viaja pelo git. Se esses arquivos existirem no Dell, vão aparecer como não
  rastreados lá. Apagá-los é decisão do Igor.
- **Os modelos salvos da v1** (`outputs/meridian/*.pkl` e `outputs/robyn/seed*/OutputCollect.rds`)
  só existem aqui, e a C12 roda os alocadores sobre eles sem refit. Não apague `outputs/`.

### O que mudou nas decisões abertas da C6

- **Publicar:** feito.
- **D5, `BACKLOG` 9:** ficou de fora; o braço melhor caso resolve pela configuração.
- **O degrau com slope 1, `BACKLOG` 8:** virou a C10.
- **O tamanho do artigo:** vale o que foi publicado. A parte 2 tem teto de 1.000 palavras
  e a parte 3, de 2.000.
- **A frase "came back identical" do README:** é corrigida no README-índice da C13.

As abertas novas estão no bloco 5 do roadmap:
- a spec do Robyn que converge (a C16 mede);
- a licença do Heusch (C17);
- o nome novo do repo (começo da C21);
- se o Pages redireciona depois do rename (C23).

### Próximo passo

C10, em qualquer máquina, perfil `dificil` (opus/high). O primeiro commit é só a emenda de
pré-registro da parte 2 no `docs/PLAN.md`; nenhum número novo pode entrar antes dela.

## Sessão C8 (24/09): licença, humanize, rodadas 10 e 11

- **Licença:** MIT no código, CC BY 4.0 no artigo (`LICENSE`, `article/LICENSE.md`,
  seção Licence no README). Escolha do Igor, 24/09.
- **Humanize** no README e no artigo: só travessão virando outra pontuação. Os
  números batem como multiconjunto antes e depois, e os qualificadores também.
- **Rodada 10** do auditor, só no diff: SHIP, com 1 achado médio e 4 leves, todos
  do mesmo mecanismo: a vírgula no lugar do travessão religou a cláusula no lugar
  errado. Corrigidos com o conserto mínimo do auditor. **Rodada 11**, nas seis
  linhas corrigidas: SHIP, nada a reportar. Registro em `analysis/AUDIT.md`.
- **Clone limpo nesta máquina (Dell, `C:\Users\igorlima`):** as seis chamadas da
  camada 1 saem com 0 em 41 s, e `summary.md`, as três figuras e os 20 arquivos de
  dados voltam idênticos. **Mas 8 JSONs do oráculo diferem no 16º dígito**
  (`r2` 0.8052827723838654 vira ...657, por exemplo), e `git diff --ignore-cr-at-eol`
  não volta 0. É ruído de ponto flutuante entre máquinas, e não mexe em número
  publicado. O parágrafo "Verified, not asserted" do README descreve o passe de
  11/09 e continua verdadeiro sobre ele, mas "every regenerated tracked artifact
  came back identical" **não vale em qualquer máquina**. Não corrigi: é decisão do
  Igor se o README passa a dizer isso. O tempo também variou (41 s aqui, contra
  "about 10–15 seconds").
- **Pegadinha do Windows:** venv em caminho comprido (o scratchpad) quebra o
  `pip install` do numpy com `WinError 206`. Clone num caminho curto (`%TEMP%\mmc`).

## Sessão C6 (10-11/09) — a auditoria adversarial, nove rodadas até SHIP

Karen, mas quase nada precisou dela: só a conferência dos priors do Meridian
usou o venv WSL2 (ver "Preso a esta máquina"). O resto roda igual no Dell.

### O que foi feito

Nove rodadas do `publication-auditor`. Sete voltaram BLOCK, duas SHIP — a 6ª e,
depois de uma checagem de regressão, a 9ª. O registro público está em
**`analysis/AUDIT.md`** (última linha `VERDICT: SHIP`), linkado do mapa do
README. Vinte arquivos mudaram; os que importam:

- **`analysis/scoring.py`** — emite a comparação nas mesmas seeds quando um
  braço roda num subconjunto das seeds de outro. É de lá que sai o 0.470.
- **`analysis/figures.py`** — `curve_facts()` e `roi_facts()`: as legendas das
  figs 1 e 2 agora **calculam** os números que citam e **afirmam** as frases
  qualitativas que fazem. Se uma re-exportação invalidar qualquer uma, a figura
  não é gerada. Testei os dois com sabotagem proposital; disparam nomeando a
  afirmação quebrada.
- **`article/`, `README.md`, `analysis/ORACLE.md`, `analysis/FIGURES.md`** — o
  texto todo, incluindo o reenquadramento descrito abaixo.
- **`docs/PLAN.md`, `runs/*/DECISIONS.md`, `simulation/config.py`,
  `data/README.md`** — emendas datadas de 11/09. Nenhuma pré-registração foi
  reescrita; a original fica e a emenda entra embaixo.

Três achados mudaram a substância, não a redação:

1. **Geo contra nacional era artefato de composição.** O artigo dizia que o geo
   tinha o agregado melhor (0.499 contra 0.533). Mas 0.499 é média de 2 seeds e
   0.533 de 5; nas mesmas duas seeds o nacional marca **0.470** — o geo é pior.
2. **A D5 se contradisse desde o primeiro commit.** Ela exigia a verdade dentro
   dos limites recomendados do Robyn ("truth outside would rig the test"), e a
   tabela de parâmetros do mesmo commit pôs ooh em 0.6 (limite 0.1–0.4) e display
   em 0.4 (limite 0–0.3). O Robyn não conseguia expressar o carryover verdadeiro
   nesses dois canais.
3. **A inclinação do Hill do Meridian é fixa em 1** (`slope_m` é
   `Deterministic(1.0)` no 1.8.0; confirmei instanciando no venv da Karen, e os
   extratos geo confirmam — não há `slope_m` no `rhat_by_param`). O plano
   chamava isso de prior "concave-leaning". Com inclinação fixa, o Meridian não
   representa o S do tv.

Por causa de 2 e 3, a peça saiu de "as duas foram tratadas com generosidade"
para **"o setup de cada ferramenta excluiu parte da verdade"**, com as duas
exclusões declaradas onde os números aparecem — inclusive nas legendas.

### O que foi tentado e falhou — não repita

- **Auditor de escopo amplo estoura o limite de 40 turnos e volta sem veredito.**
  Aconteceu na primeira chamada desta sessão (51 tool uses, 111k tokens, nenhum
  veredito) exatamente como o C3 e o C4 já tinham avisado. O que funciona:
  escopo estreito **e** instrução explícita de reservar orçamento para escrever
  o veredito antes de acabar.
- **`SendMessage` não existe neste build.** Subagente que estourou não se
  retoma; tem de relançar. Não perca tempo procurando.
- **Três subagentes em paralelo estouraram o limite de sessão** (429, duas
  vezes, perdendo as três chamadas de uma vez). Rodar **em série**.
- **O hook `git-destrutivo` bloqueia `git clean`**, inclusive em clone de
  rascunho no scratchpad. Está certo. A saída é clonar de novo, não contornar.
- **O erro mais caro fui eu.** Os bloqueantes das rodadas 2, 3, 6, 7 e 8 foram
  introduzidos pelas minhas próprias correções. Dois padrões: (a) número
  publicado sem fonte commitada; (b) **adjetivo de distância aplicado a um grupo
  de números** — "within 0.02" para um gap de 0.0208, "well below" para um canal
  a 0.026. O que resolveu: **listar os números em vez de adjetivar**, e calcular
  cada um antes de escrever. A última rodada pegou ainda um "a mediana" que, no
  meio de uma frase sobre cinco médias, se lia como a mediana delas (1.06) e não
  a do prior (1.22) — a palavra "prior" era obrigatória.

### Reprodutibilidade, re-verificada no estado final

Não reaproveitei o passe do C5: clone novo, venv construído do zero só com
`envs/analysis.lock.txt`, as seis chamadas da camada 1, e comparação byte a
byte. **14.2 s**, conteúdo idêntico a menos de CRLF, os três PNGs bit a bit,
42 arquivos listados pelo git. O README teve de mudar de "under 15 seconds"
para "about 10–15 seconds": as medições variaram de 10 a 15 s, e afirmação
publicada não pode depender do relógio estar de bom humor.

### Preso a esta máquina

Só uma coisa: a conferência dos priors do Meridian (`slope_m`, `alpha_m`,
`roi_m`) foi feita instanciando `PriorDistribution()` no venv WSL2 da Karen.
O resultado está escrito nas emendas e no `AUDIT.md`, então **não precisa ser
refeito** — mas quem quiser repetir precisa da Karen.

### Decisões do Igor que continuam abertas

1. **Não existe `LICENSE`.** Herdado do C5 e ainda em pé. O auditor não cobre
   licenciamento, então ele nunca ia pegar isso. Repo público sem licença é repo
   que ninguém pode reusar legalmente. É a primeira coisa da próxima fatia.
2. **Publicar virou decisão de data**, não de estado: a peça está em SHIP.
3. **Declarar ou regerar a contradição da D5** (`docs/BACKLOG.md` item 9).
   Regerar muda todos os números. Escolhi declarar; a escolha é reversível.
4. **Degrau do oráculo com inclinação fixa em 1** (`BACKLOG` item 8): mediria
   quanto do erro do Meridian vem da inclinação. Não rodei — é análise nova.
5. **O artigo foi de 1.299 para 1.835 palavras**, acima da faixa de 800–1300 do
   `verificar:` do C4. Todo o acréscimo é ressalva que a auditoria exigiu. Há
   nota datada no `ROADMAP` registrando isso.

## Sessão C5 (10/09) — README público e o passe de reprodutibilidade

Karen (RTX 4070 Super), mas **nada aqui precisou de GPU, WSL2 ou R** — de
propósito: a fatia inteira existe para provar que a camada de análise não
precisa deles. Roda igual no Dell.

### O que foi feito

**`README.md`, 8 → ~215 linhas.** Reescrito para quem chega de fora: a
pergunta, a resposta condicional (sem vencedor, com a tabela de agregados por
braço e a de recuperabilidade por canal, cada uma com legenda dizendo que o
dado é simulado e apontando o artefato de onde veio), `fig1` embutida, duas
camadas de reprodução, tabela de versões completa com **o pino `tfp-nightly` e
o risco dele escrito por extenso** (nightly pode ser yanked; se sumir, o
`setup_meridian.sh` para de reproduzir o ambiente destes resultados), a seção
"where 'pinned' stops being true" sobre o lado R repetida de
`envs/ENVIRONMENT.md`, o mapa do repo e um "Scope, honestly" final. O artigo
**não foi tocado** — continua nas 1.299 palavras com `VERDICT: SHIP` do C4.

**O passe do clone limpo foi executado, não afirmado.** Clone em diretório
vazio dentro do scratchpad, venv criado do zero contendo só
`envs/analysis.lock.txt`, Meridian e R fora do caminho. Os quatro comandos do
`verificar:` mais `figures.py` e `oracle.py --diagnostics`: **todos exit 0, 13 s
no total**. Mais forte que o pedido: **todo artefato rastreado voltou idêntico**
— os 20 arquivos de `data/sim/`, os 20 JSONs de `runs/oracle/results/`,
`summary.md`, `diagnostics.md` e os três PNGs (esses byte a byte, inclusive).
O check C6 de determinismo, portanto, se sustenta num ambiente que nunca viu
este repo.

**Varredura do histórico inteiro (19 commits, `git log -p --all`).** Zero
hostname (o hostname desta máquina não aparece em lugar nenhum), zero caminho
local absoluto (`C:\Users`, `/mnt/c/Users`, `/home/*`), zero segredo, zero IP.
A frase proibida aparece 4 vezes e **todas as quatro são a própria regra que a
proíbe** (BRIEF.md, CLAUDE.md, "does not claim…"). Único dado pessoal é o
e-mail de autor dos commits, que é o do Igor e é o normal num repo público sob
o nome dele.

### Duas coisas que o passe revelou e viraram correção

1. **`tzdata` não estava pinado.** É dependência transitiva do pandas no
   Windows, e um `requirements.txt` simples deixa o pip resolvê-la sozinho —
   buraco num arquivo cuja função é fechar buracos. Pinado em
   `envs/analysis.lock.txt` (`tzdata==2026.3`) com o porquê no cabeçalho, e o
   passe foi **re-rodado do zero com o lock corrigido**: o `pip list` do venv
   novo bate exatamente com o lock, e os seis comandos deram exit 0 de novo.
2. **CRLF vs LF.** O gerador escreve CRLF no Windows enquanto o git guarda os
   arquivos com LF (`.gitattributes`), então `git status` acusa os 20 CSVs/JSONs
   como modificados depois de re-gerar. **O conteúdo é idêntico** —
   `git diff --ignore-cr-at-eol --quiet` retorna 0. Isso está documentado no
   README como a forma honesta da promessa de determinismo, em vez de escondido.
   **Dá para eliminar** fazendo o gerador escrever LF explícito
   (`to_csv(..., lineterminator="\n")` e afins); não foi feito por ser fora do
   escopo do C5.

### O que quase passou batido

O README chegou a afirmar que `analysis/out/diagnostics.md` "voltou idêntico"
depois do passe — **afirmação vazia**, porque `analysis/oracle.py` só escreve
esse arquivo com a flag `--diagnostics` (sem ela o `main()` faz `return` antes
de gerar), e a sequência documentada não a tinha. Corrigido nos dois lados: o
comando entrou na sequência do README com a explicação de que `--diagnostics`
**substitui** o ajuste em vez de somar a ele, e a verificação foi refeita
apagando `diagnostics.md` no clone e regerando — volta idêntico.

### Correções de comando na camada 2 do README

`runs/meridian/run_meridian.py` exige `--arm` e `--seeds` (a primeira versão do
README passava seeds soltos, que não roda). O braço geo precisa de
`--n-adapt 2000 --n-burnin 2000` para bater com o spec dos extratos commitados.
Robyn ficou em dois comandos, 4000×5 para as seeds 101-104 e 2000×5 para a 105,
que é o spec misto real — está dito no README, não escondido.

### Nada ficou pela metade, e nada está preso a esta máquina

O clone de teste vive no scratchpad da sessão e é descartável. Nenhum run
pesado foi iniciado.

### Duas decisões que são do Igor e o C6 vai cobrar

- **Não existe `LICENSE`.** Repo público sem licença é repo que ninguém pode
  reusar legalmente. A escolha é dele.
- **O README não diz mais "work in progress".** O texto está terminado, então
  publicar virou decisão de data, não de estado — mas a auditoria do C6 ainda
  não passou sobre ele.


## Sessão C4 (10/09) — Fase 6: o artigo, e o que três auditorias forçaram

Karen (RTX 4070 Super), mas **nada aqui precisou de GPU, WSL2 ou R** — C4 é
escrita sobre arquivos commitados e roda no Dell igual.

**O que foi feito.** `article/meridian-vs-robyn.md` (novo), **1.299 palavras**,
`VERDICT: SHIP` do `publication-auditor`. Estrutura: setup → o empate que não é
o resultado → recuperabilidade por canal → ler a tabela de erro da própria
ferramenta inverte a resposta → intervalos → guia de decisão condicional →
"What neither tool can tell you" → reprodução. Os cinco itens do `verificar:`
do C4 foram conferidos um a um e passam.

**Efeito colateral que virou correção de raiz.** A coluna signal/noise do
artigo (tv 1.91 … display 0.10) só existia no **stdout** de `oracle.py
--diagnostics` — não em `summary.md` nem em JSON. Isso reprovaria o "todo
número traça para artefato commitado". `analysis/oracle.py` agora **escreve**
`analysis/out/diagnostics.md` (negação explícita no `.gitignore`), e o
`analysis/ORACLE.md` ganhou um parágrafo dizendo qual documento é fonte de quê
— fecha também a observação não-bloqueante da primeira auditoria desta sessão.

**Gates:** os três passaram e **nada se moveu** — `analysis/out/summary.md` e
os 20 JSONs de `runs/oracle/results/` saíram byte-idênticos aos commitados,
confirmado por `git status` limpo nesses caminhos depois de re-rodar. Figuras
**não** foram redesenhadas, de propósito: nenhum valor plotado mudou.

### A auditoria reprovou duas vezes. As 13 correções eram todas reais.

Três rodadas estreitas (15, 17 e 7 chamadas — todas com veredito; a forma ampla
continua estourando o limite de turnos, como no C3). A primeira, sobre o estado
**commitado** do C3, deu SHIP com zero mismatches — a pendência que o C3 deixou
está encerrada. As duas seguintes, sobre o artigo, deram BLOCK. O que importa
para quem continuar:

- **O número mais citável do artigo estava inflado, e a favor da nossa tese.**
  O guia comparava "Meridian 432s × Robyn 1017s". A média do Robyn é dominada
  por **quatro runs escalados a 4000×5**; o único seed na spec pré-registrada
  (105) rodou **566,4s**. Na spec pré-registrada a diferença é 1,3×, não 2,4×.
  Pior: a ressalva de spec mista dizia "every Robyn number **above**" e o bullet
  de runtime ficava **abaixo** dela — a ressalva estava onde o número não
  estava. Regra que sai daí: **ressalva com escopo posicional ("acima",
  "a seguir") é ressalva que vaza.** Trocado por "here".
- **Eu quebrei o guardrail que o próprio artigo enuncia.** O texto manda ler
  ooh e display como empatados em "não recuperável", nunca ordenados — e sete
  linhas depois chamava ooh de "the least recoverable channel here", ordem que
  a **própria tabela do artigo** contradiz (display 0.10 abaixo de ooh 0.11).
- **"Upper bound" sobre um erro lê ao contrário.** Eu escrevia que o spend
  exógeno faz de cada número "an upper bound" — sobre um *erro*, isso diz que
  dado real erraria menos, o oposto do pretendido. Virou "flatters both tools".
- **Uma afirmação contradizia o corpo do próprio artigo:** o bullet de
  limitações dizia que *as duas* ferramentas parecem melhores nos canais não
  mensuráveis. Falso para o braço **national** do Meridian, cujo melhor canal é
  tv (0.336), o mais recuperável — lá há achatamento, não inversão. O
  `ORACLE.md` já dizia isso; eu não segui. Escopo corrigido para Robyn + geo do
  Meridian.
- **Erros meus pegos antes da auditoria, na conferência contra `summary.md`:**
  eu havia escrito que as cinco células menores que o `ooh 0.161` eram "todas
  em tv" (são quatro em tv e uma em search) e que o braço geo do Meridian
  **não** tinha batido o national (bateu: 0.499 × 0.533 — o que muda o
  argumento e agora aparece qualificado pelos dois seeds e pelo não-convergido).
- Menores, todos corrigidos: `8.69pp` sem dizer de qual rung (é o L3), o
  `ooh 0.161` sem a ressalva dos dois seeds **inline**, um número de run
  não-convergido dentro de uma **recomendação**, e `analysis/ORACLE.md`
  ausente da lista de fontes.

### O que foi tentado e falhou — não repita

- **Heredoc `<<'PYEOF'` com `
` dentro de string Python falhou de novo**,
  mesmo com o delimitador entre aspas. O bloco grande não casou e o `assert`
  abortou (corretamente, sem gravar nada). **O que funcionou:** editar por
  **intervalo de linhas**, localizando início e fim por âncora e imprimindo as
  linhas encontradas antes de substituir; e construir o backslash-n com
  `chr(92) + "n"` quando ele precisa aparecer no código gerado. Isso refina a
  fricção já registrada no C3 — o problema não é só a expansão do heredoc.
- **Cortar palavras por passadas incrementais é desperdício.** Foram **sete**
  passadas para tirar ~560 palavras (1858 → 1299), e as passadas de aperto de
  frase rendiam 5 a 20 palavras cada. O que rendeu de verdade foi cortar
  **conteúdo**: transformar a tabela de bandas em prosa, encolher a seção de
  reprodução, remover repetição entre título de seção e primeiro parágrafo.
  Da próxima vez: medir primeiro, decidir o que **sai**, e só então redigir.
- **Reenviar o artigo ao Igor a cada revisão não foi feito de propósito** — só
  duas entregas, o primeiro rascunho e o final. Cada correção intermediária
  teria sido ruído.

### Pendências que o C5 herda

- **O SHIP era condicional a `analysis/out/diagnostics.md` entrar no mesmo
  commit que o artigo** — senão a frase "traces to a committed artifact" fica
  falsa. Este commit resolve; se alguém reverter o `.gitignore`, a frase volta
  a ser mentira.
- **O artigo tem 1 palavra de folga** até o teto de 1300 do `verificar:` do C4.
  Qualquer acréscimo estoura. Se precisar acrescentar, corte antes.
- **Os literais de legenda em `figures.py` continuam à mão** (lista exaustiva
  em `analysis/FIGURES.md`). Nada mudou aqui, mas o risco segue.
- **O lado R continua não pinado** — e agora é obrigação do README do C5 dizer
  isso, não só do `envs/ENVIRONMENT.md`.
- O `docs/BACKLOG.md` não foi tocado nesta sessão.

**Nada preso a esta máquina.** C5 é escrita mais um clone limpo com Python
puro — roda no Dell sem admin.


## Sessão C3 (09/09) — Fase 5: scoring, os três gráficos, e oito rodadas de auditoria

Karen (RTX 4070 Super), mas **nada aqui precisou de GPU, WSL2 ou R** — C3 é
Python puro sobre arquivos commitados e roda no Dell igual.

**O que foi feito.** `analysis/figures.py` (novo) desenha os três gráficos da
Fase 5 em `analysis/figures/`; ele chama `scoring.run_scoring()` em vez de
recalcular, e importa `simulation.checks.channel_snr` para ordenar os canais,
de modo que gráfico e gate C7 não conseguem divergir. Para isso o cálculo do
C7 virou função reutilizável em `simulation/checks.py` (saída idêntica,
verificada). `analysis/FIGURES.md` (novo) registra as seis decisões de desenho
(D-F1..D-F6). `docs/PLAN.md` Fase 5 fechada. `envs/analysis.lock.txt` (novo)
pina a camada de análise — matplotlib era a dependência que faltava — e
`envs/ENVIRONMENT.md` ganhou a seção correspondente.

**Decisão de desenho que manda no resto:** a terceira série dos gráficos 1 e 2
é o oráculo **L3** (estima o próprio baseline, como as duas ferramentas
precisam fazer), não o L2. O `analysis/ORACLE.md` continua usando L2 na tabela
por canal, porque lá a pergunta é de teto ("era recuperável por alguém?"). Os
dois documentos agora explicam essa divisão em vez de se contradizerem.

**O scorer mudou e o `summary.md` ficou mais informativo.** `analysis/scoring.py`
agora imprime, por tool-arm: quantos seeds passaram no check de convergência da
própria ferramenta, a **spec de run** (lida de `run.convergence_detail` — Robyn
em iterations x trials, Meridian em adapt/burnin, com aviso explícito quando a
spec é mista) e, por canal, o erro relativo **com sinal e absoluto** mais a
coluna `effect share − spend share (pp)`. Nada disso altera M1–M5; o
`rssd_pull` pré-registrado ficou intocado.

### A auditoria reprovou oito vezes. Leia isto antes do C4.

Rodei o `publication-auditor` oito vezes: BLOCK com 6, 2, 1, 2, (sem veredito),
(sem veredito), 1 e 3 achados. **Todos os achados numéricos eram reais.** Os
que importam para quem continuar:

- **A coluna do Robyn no `ORACLE.md` estava desatualizada** desde a escalada do
  C1: cobertura 0.20 → **0.16**, viés −0.506 → **−0.540**, |erro| 0.538 →
  **0.555**, e todos os cinco erros por canal mudaram. A afirmação "search e tv
  são os piores do Robyn" ficou falsa (são search e social).
- **A história de convergência do Robyn estava errada por um seed.** O
  `runs/robyn/DECISIONS.md` registra **quatro** seeds falhando a 2000×5; o
  seed101 só convergiu depois da escalada. E os extratos commitados são **spec
  mista** (101–104 a 4000×5, 105 a 2000×5) — coisa que não estava em lugar
  nenhum e agora viaja nas três legendas e no `summary.md`.
- **Assimetria de divulgação, e era contra nós.** As ressalvas do Robyn estavam
  em todo lugar; as do Meridian, em lugar nenhum. O braço **geo** do Meridian
  rodou a **2000/2000** (4x a spec pré-registrada, terceira tentativa) com
  **64 e 122 divergências** contra 1–6 por run national, e o seed102 conta como
  convergido carregando 122. O `runs/meridian/DECISIONS.md` registrava
  divergências das tentativas **descartadas** e nunca das publicadas — corrigido
  por emenda datada, lida dos extratos, sem re-run.
- **A inversão aparece nas DUAS ferramentas.** O braço geo do Meridian inverte
  por completo: ooh **0.161** é o canal mais preciso dele e o menor erro por
  canal que qualquer uma das duas ferramentas alcança — em cima do canal menos
  recuperável do cenário. As cinco células menores da tabela são todas do
  oráculo — quatro em tv e uma em search (corrigido em 11/09, na auditoria do
  C6: aqui dizia "todas em tv"). Isso muda o enquadramento do artigo e é o gancho mais
  forte do C4.
- **O dial de correlação tv–ooh nunca acertou o alvo.** Realizado 0.34, 0.37,
  0.38, 0.38, 0.61 contra alvo pré-registrado de ~0.4–0.5: **zero de cinco**
  dentro. O que segurou os dados foi o gate C2, mais largo, [0.30, 0.65].
- **O mecanismo de encolhimento estava mal descrito.** "Cada ferramenta encolhe
  para um valor característico" não descreve o Meridian: ele **comprime** para
  a banda 0.74–1.24 (fator 1.7 contra 4.4 da verdade), com a mediana do prior
  (1.22) perto do topo da banda (1.24), não no centro — corrigido em 11/09, na
  auditoria do C6: aqui dizia "no **teto**", e a média de ooh passa dela. O Robyn sim colapsa: banda
  0.68–0.73, fator 1.08.

### O que foi tentado e falhou — não repita

- **Script de patch que faz vários `replace` e grava só no fim.** Uma asserção
  falha no meio e **descarta as edições anteriores**, silenciosamente. Isso
  aconteceu duas vezes e nas duas eu relatei correções que não existiam no
  disco. Regra que sai daí: **um arquivo por script, e `grep` de verificação
  depois de gravar** — nunca confiar no "ok" impresso.
- **`replace()` sem asserção.** Um `s.replace(a, b)` que não casa imprime "ok" e
  não faz nada. Toda substituição precisa de `assert a in s`.
- **Heredoc do Bash com `
` dentro de string Python:** o `
` chega como
  newline real e a busca nunca casa. Construir com `chr(92) + "n"`.
- **Auditoria ampla estoura o limite de 40 turnos sem dar veredito** — aconteceu
  duas vezes seguidas, ~200k tokens sem resultado. **Auditoria estreita** (três
  arquivos, uma pergunta, orçamento de turnos declarado, "veredito parcial se
  faltar turno") deu veredito em 15–25 chamadas. Usar só essa forma.
- **`SendMessage` para subagente não existe neste build** — não dá para retomar
  um auditor que estourou o limite; só relançar.
- **Média entre seeds antes do módulo cancela sinal e lisonjeia.** Foi assim que
  publiquei "0.4pp" onde o valor honesto por célula canal-seed é **0.54pp**.
  Agregação sempre por célula, e a agregação usada tem de estar dita.

### Pendências que o C4 herda

- **Uma auditoria só teve veredito parcial.** O último BLOCK tinha 3 achados;
  dois foram corrigidos e o terceiro era "os arquivos novos estão untracked",
  que este commit resolve por construção. **Não houve rodada de auditoria sobre
  o estado commitado** — vale rodar uma estreita no início do C4.
- **A limitação do M5 está documentada, não corrigida.** O `rssd_pull` pontua o
  Meridian (0.085) acima do Robyn (0.067) porque mede deslocamento sem teto: o
  Meridian passa do spend share, o Robyn pousa em cima. A métrica ficou como
  pré-registrada e a coluna nova `effect share − spend share` foi posta ao lado.
- **Números na prosa das legendas são literais escritos à mão** em
  `figures.py` (64, 122, 2000/2000, 4000x5, 92%, as razões da curva de tv, as
  versões das ferramentas). Foram lidos dos JSONs commitados, mas **nada no
  pipeline pega um literal obsoleto** se um run for re-exportado. Lista
  exaustiva no `analysis/FIGURES.md`.
- **O lado R não é pinado** (`install.packages("Robyn")` sem versão;
  `nevergrad.lock.txt` é escrito pelo script, não lido). Dito em dois lugares e
  virou item 7 do `docs/BACKLOG.md`.
- **`docs/REASSESSMENT_2026-09-08.md` ganhou nota de snapshot** em vez de ser
  reescrito: os números do Robyn nele estão superados, e a nota diz para onde ir.
- O mini-arm de sensibilidade da Fase 5 foi **descartado da v1** de propósito
  (o oráculo responde a mesma pergunta com cinco seeds, e re-rodar ferramenta
  depois de ver resultado é o que a pré-registração existe para impedir). Item
  6 do backlog, para a v2, pré-registrado.

**Nada preso a esta máquina.** C4 é escrita e roda em qualquer PC.


## Sessão C2 (09/09) — gate de sinal/ruído por canal, C2 fechado

Mesma máquina da sessão C1 anterior (Karen, RTX 4070 Super). Trabalho
puramente de código/docs, não precisou de GPU nem de WSL2.

**O que foi feito:** adicionado o check **C7** em `simulation/checks.py` —
sinal-to-noise por canal (desvio padrão da contribuição nacional verdadeira do
canal / desvio padrão do ruído de receita nacional, janela de medição), com
piso `SNR_FLOOR = 0.15` definido no topo do módulo. É **WARN, nunca FAIL**:
imprime uma linha por canal por seed e só adiciona a warnings list se abaixo
do piso — nunca ao `failures`, então nunca derruba o exit code.

Rodei `python -m simulation.checks` nos 5 seeds: exit 0 em todos, e os
números batem com `analysis/ORACLE.md` (tv ~1.7-2.1, search ~0.34-0.46, social
~0.31-0.37 — todos acima do piso; ooh ~0.09-0.12 e display ~0.09-0.11 — os
dois abaixo do piso, em **todo** seed, sem exceção). Isso é exatamente o
achado que o oráculo já tinha isolado por outro caminho (fit OLS com os
parâmetros verdadeiros) — o gate barato concorda com o gate caro.

Documentei o gate em `docs/PLAN.md` §3 (novo parágrafo depois do bullet de
"Simulator checks") e `data/README.md` (nova seção depois da variance share),
os dois citando `analysis/oracle.py` como o passo de verdade-terreno
pré-registrado que qualquer cenário futuro deve rodar antes de comprometer
uma GPU — deixei explícito que C7 é um proxy barato, não substitui o oráculo.

**Nada ficou pela metade.** Não houve nada tentado e abandonado nesta
sessão — a mudança era pequena e totalmente especificada no `docs/PROXIMO.md`,
rodou de primeira.

**Verificação do `verificar:`** confirmada linha a linha:
`python -m simulation.checks` → exit 0; `grep -c 'signal-to-noise' docs/PLAN.md
data/README.md` → `1` e `2` (ambos não-zero).

**Arquivos tocados:** `simulation/checks.py`, `docs/PLAN.md`, `data/README.md`.
Nenhum dado gerado foi tocado (`data/sim/` não muda com este check).

`docs/ROADMAP.md`: C2 → `done`. `docs/PROXIMO.md` avançou para **C3** —
opus/high (julgamento analítico), já desbloqueado desde que C1 fechou na
sessão anterior. Nada preso a esta máquina: C3 é escrita e análise, roda em
qualquer PC.

## Sessão C1, retomada (09/09) — C1 fechado, escalada não resolveu convergência

Reabri no mesmo dia, mesma máquina (Karen, RTX 4070 Super confirmada de novo).
Rodei a escalada 4000×5 para os seeds 102, 103 e 104 com o comando corrigido
(`bash -lc "cd ... && ..."` em vez de `wsl --cd`) — terminou em ~1h,
desatendido, sem erro.

**Resultado, e é um achado, não um problema:** os três seeds rodaram os 4000
iterações completas, mas **nenhum convergiu** pelo critério próprio do Robyn
(DECOMP.RSSD falhou nos três; NRMSE falhou só no 102). Dobrar as iterações não
resolveu a não-convergência que já tinha sido documentada a 2000×5. Estado
final dos cinco seeds do Robyn: 101 convergido (4000×5), 102/103/104 não
convergidos (4000×5), 105 convergido (2000×5, spec original, nunca escalado).
Fechei a emenda RD em `runs/robyn/DECISIONS.md` com os números exatos de cada
seed (sd/med do DECOMP.RSSD e NRMSE, runtime).

Rodei os três gates (`/score`): todos passaram limpo. A cobertura do intervalo
do Robyn nacional caiu de ~20% (estimativa anterior, pré-escalada) para
**16%** com o dado final. `analysis/out/summary.md` foi regenerado e
commitado.

`docs/ROADMAP.md`: C1 → `done`. C3 também desbloqueou (dependia só do C1), mas
o ponteiro `docs/PROXIMO.md` avançou para **C2** — mesmo perfil mecânico
(sonnet/medium) desta sessão, roda em qualquer máquina, sem pré-requisito. C3
é opus/high (julgamento analítico) e fica pra quando o Igor pedir
explicitamente.

**Também nesta sessão:** o Igor levantou três perguntas sobre o desenho do
dataset (granularidade de canal por veículo digital, uso do reach&frequency
nativo do Meridian, o fato de eu ter dito impreciso que "nenhuma ferramenta
modela frequência" — o Meridian aceita um tipo de canal RF, só não foi usado
aqui de propósito, pra manter a comparação like-for-like). Viraram os itens 4
e 5 do `docs/BACKLOG.md` (v2, pós-publicação), em vez de mudar o `docs/PLAN.md`
da v1.

## Sessão C1, primeira tentativa (09/09) — escalada interrompida, nada perdido

Esta sessão tentou rodar a escalada 4000x5 do Robyn para os seeds 102, 103 e
104 (a pendência do C1). O run foi **interrompido antes de terminar** porque a
máquina (Karen) precisa ser desligada. **Nenhum JSON foi escrito** — o processo
foi morto durante o feature engineering do seed102 (~1% do trabalho de um
único seed), então `runs/robyn/results/` está exatamente como estava:
seed101 em 4000x5, seeds 102–105 em 2000x5. `git status` limpo, nada para
reverter.

**Fricção nova, documentada para não ser redescoberta:** `wsl -d Ubuntu -u igor
--cd <path> -- <comando>` funciona em **foreground** mas falha em
**background** com `WSL/ERROR_PATH_NOT_FOUND` (código de saída 127) — testado
três vezes, inclusive com um comando trivial (`pwd`) sem nada de específico do
Robyn. A forma que funciona em background é trocar o flag `--cd` por
`bash -lc "cd <path> && <comando>"`. `docs/PROXIMO.md` já foi atualizado com o
comando corrigido.

**Próximo passo, ao reabrir nesta máquina:** rodar de novo o comando corrigido
em `docs/PROXIMO.md` para os três seeds (102, 103, 104) — nenhum progresso
parcial existe para aproveitar, é um restart limpo. `docs/ROADMAP.md` marca o
C1 como `doing` (não `next`) para deixar claro que já foi tentado uma vez. O
ponteiro `docs/PROXIMO.md` **não avançou** — o `verificar:` do C1 continua
insatisfeito.

## Onde estamos

**Fases 1, 3 e 4 concluídas** (a 4 com uma pendência de escalada). Esta sessão
não rodou modelo nenhum: ela reavaliou o projeto depois do lançamento do
Meridian GeoX, construiu o teste que faltava para a peça ser publicável, e
montou a infraestrutura de Claude Code do repo.

A partir de agora a **fila de trabalho vive no `docs/ROADMAP.md`** (C0–C6, com
máquina, modelo e esforço recomendados por tarefa). Este arquivo continua sendo
a narrativa: o que falhou, o que ficou pela metade, o que está preso a esta
máquina. O `/oi` lê só a tabela do roadmap; este documento é lido sob demanda.

## O que esta sessão fez

**1. Reavaliação 360 → `docs/REASSESSMENT_2026-09-08.md`.** Reverificação de
Meridian, Robyn, GeoX, GeoLift e PyMC-Marketing contra fontes primárias em
08/09. O que mudou desde o planejamento de 27/08:

- **Meridian 2.0.0 saiu em 03/09** (mudou o backend padrão de TensorFlow para
  JAX, mais 6 breaking changes). Os runs deste repo são **1.8.0** — decisão:
  ficar na 1.8.0 para a v1 e tratar a defasagem como achado sobre churn de
  ferramenta, não como dívida.
- **Meridian GeoX foi 0.1.1 → 1.0.0 → 1.0.1 em 48 h.** O extra de instalação
  funciona; o nome correto é `geox` (`pip install "google-meridian[geox]"`),
  não `meridian-geox`. Decisão: **sem braço GeoX na v1** — exigiria subir para
  2.0.0 e re-rodar tudo, e o Robyn só aceita point-estimate como calibração, o
  que transformaria a comparação em demo de feature do Meridian.
- **Robyn:** último commit no `main` em 27/06/2025, CRAN 3.12.1 em 02/07/2025,
  não arquivado. Estrelas: Meridian 1522 × Robyn 1513 — passou, mas por nove.
  A afirmação defensável é sobre cadência de manutenção, não popularidade.
- **PyMC-Marketing chegou a 1.0.0 estável em 07/08/2026** (backlog v2 fica mais
  barato e mais credível, mas continua fora da v1).
- **Heusch (arXiv 2608.21128, 21/08/2026) NÃO rodou as ferramentas** — ele
  implementou o próprio modelo observacional. O gap que este projeto ocupa
  continua aberto.

**2. O oráculo — o teste que faltava.** `analysis/oracle.py` +
`analysis/ORACLE.md` + `runs/oracle/results/` (20 JSONs, 4 degraus × 5 seeds,
no mesmo schema, pontuados pelo mesmo harness).

Motivo: as duas ferramentas erraram o ROI em ~50% na mesma direção, e isso é
indistinguível de um bug nosso na ground truth. O oráculo recebe a forma
funcional e os parâmetros verdadeiros e só estima os betas.

- **O harness está limpo:** com receita sem ruído, o oráculo recupera os betas
  com erro máximo de 1,2e-14. Gerador, ground truth, schema e scorer concordam.
- **Recuperabilidade é por canal.** tv (sinal/ruído 1,91), search (0,39) e
  social (0,34) são recuperáveis — o oráculo erra 4%, 15% e 24%, e as
  ferramentas erram 34–76%. ooh (0,11) e display (0,10) **não são** — o oráculo
  erra 97% e 76%, e nenhum estimador faria melhor.
- **A armadilha:** as ferramentas *parecem* melhores justamente em ooh e
  display, porque os ROIs verdadeiros ali (0,8 e 1,2) estão perto do valor para
  onde cada uma encolhe. Ler a tabela de erro de uma ferramenta sozinha inverte
  a ordem — completamente no Robyn, parcialmente no Meridian.
- **O encolhimento é das ferramentas:** viés do oráculo −0,01 a +0,12; Meridian
  −0,31; Robyn −0,51. E o degrau do oráculo que estima o próprio baseline cobre
  a verdade 92% das vezes contra 90% nominal, enquanto Meridian cobre 60% e
  Robyn 20% — "o dado era difícil" não desculpa.

Consequência para a peça: a tese deixa de ser "qual ferramenta chegou mais
perto" (empate técnico: 0,533 × 0,538) e passa a ser "a verdade estava nos
dados? em quais canais? e o que cada ferramenta faz quando não estava".

**3. Infraestrutura Claude Code (C0).** `.claude/settings.json`, dois hooks,
o subagente `publication-auditor`, a skill `/score`, o `docs/ROADMAP.md`, e `/oi` e
`/tchau` reescritos junto com as seções correspondentes do `CLAUDE.md`.

## O que foi tentado e falhou — leia antes de repetir

- **O `.gitignore` engolia toda a infraestrutura.** Ele terminava com
  `.claude/*` + `!.claude/commands/`, então `settings.json`, `agents/`,
  `skills/` e `hooks/` seriam ignorados e **nunca chegariam à outra máquina**.
  Corrigido com negações explícitas. Verificado com `git check-ignore -v`.
- **`!analysis/out/summary.csv` não funcionava** sob `analysis/out/`: o git não
  desce em diretório excluído, então negação lá dentro nunca vale. A regra teve
  de virar `analysis/out/*` (o conteúdo, não o diretório).
- **Prometi `analysis/out/summary.csv` e o scorer gera `summary.md`.** Alinhado
  para o arquivo que existe de verdade, em quatro lugares.
- **O hook de commit bloqueou meu próprio comando de teste**, porque a string
  de teste continha a frase proibida e o matcher pegou. Os testes tiveram de
  montar a frase em runtime. É a prova mais forte de que ele funciona.
- **`attribution` não existe na doc de settings.** Procurei a página inteira:
  nenhum campo controla o trailer `Co-Authored-By`. Não gravei campo não
  verificado — o default já mantém o trailer, que é o comportamento desejado.
- **`.git/index.lock` órfão de 31/08**, 0 bytes, sem processo git — resíduo de
  um dos reboots registrados no handoff anterior. **Ele teria feito o `/tchau`
  falhar.** Removido. Se `git add` reclamar de lock, cheque a data do arquivo e
  se há processo git antes de remover.
- **A auditoria adversarial reprovou o meu próprio trabalho** — ver abaixo.

## A auditoria que reprovou o ORACLE.md (e o que foi corrigido)

Rodei o `publication-auditor` contra o `analysis/ORACLE.md` recém-escrito:
`VERDICT: BLOCK`, 7 achados bloqueantes, todos verificados e reais:

1. **A coluna "Meridian" na tabela por canal misturava os braços national e
   geo**, enquanto oráculo e Robyn eram national-only — denominador diferente
   para uma ferramenta numa comparação de três, e o pool incluía um run não
   convergido. Corrigido para national-only. O ooh do Meridian é **0,55**, não
   0,44, o que enfraquece parte da afirmação original sobre "melhores canais".
   **O mesmo erro estava no `REASSESSMENT`** e foi corrigido lá também.
2. **"57–76%"** era 34–76%: o piso escolhido inflava a falha das ferramentas.
3. **Convergência subdeclarada.** Eu citava só Meridian geo seed101. São
   **quatro** runs: mais Robyn national 102, 103 e 104. Usar "Robyn cobre 20%"
   como evidência sem dizer que 3 dos 5 seeds não convergiram era exatamente a
   acusação de cherry-picking que este projeto existe para evitar. Rotulado em
   todo lugar onde número do Robyn aparece.
4. **Proveniência.** Sinal/ruído, CV do regressor, correlações e o teste sem
   ruído não saíam de nenhum script commitado — foram gerados no terminal.
   Violação direta da regra dura nº 3. Corrigido na raiz: `python
   analysis/oracle.py --diagnostics` agora emite todos eles.
5. **Ao regenerar, as correlações publicadas estavam erradas:** eu disse
   0,79–0,95 (é **0,66–0,94**) e 0,02–0,24 para os demais pares (é **−0,05 a
   0,09**, com um par negativo, ooh–search, que eu havia omitido).
6. Viés do oráculo "+0,07 a +0,12" contradizia a própria tabela (L3 = −0,008).
7. Citação errada (`PLAN D5` onde é `PLAN §3`), √8 onde é √6, e "erro 0,0" onde
   é 1,2e-14.

**Lição para as próximas sessões:** rodar o auditor **antes** de considerar
qualquer texto pronto, não depois. Ele achou erro numérico real em documento
que eu tinha acabado de escrever e revisar.

## Colisão com o canon do playbook — resolvida, leia antes de mexer em `.claude/`

No fim desta sessão o push foi **rejeitado**: o commit `2d3fd21` ("instala o
canon do playbook") tinha subido do outro lado enquanto o trabalho corria, e
colidia com a infraestrutura recém-construída em quatro arquivos.

Resolução, decidida pelo Igor e aplicada por rebase (`eb8fd1f`):

- **O canon vence nos comandos.** `/oi`, `/tchau`, `/360`, `hooks/sessao-abre.ps1`
  e `.gitattributes` ficaram **idênticos** ao canon — verificado com
  `git diff origin/main -- <arquivo>` em cada um. As versões que esta sessão
  havia escrito para `/oi` e `/tchau` foram descartadas.
- **`settings.json` virou união:** os `deny` do canon (que incluem
  `git reset --hard` e `git clean -fd`, que a versão local não tinha) mais os
  `allow` dos três gates de Python, `git push` em `ask`, os caminhos de chaves
  negados, `PYTHONUTF8=1`, e os **três** hooks convivendo (o `SessionStart` do
  canon + os dois desta sessão).
- **`.gitignore`:** as duas versões tinham feito **a mesma correção de forma
  independente** (negações para `.claude/settings.json|skills|agents|hooks`).
  Ficou a do canon, que ainda ignora `settings.local.json` explicitamente.
- **O que é só deste repo ficou por cima:** `guard_publication.py`,
  `warn_py_syntax.py`, `publication-auditor`, a skill `/score`, o oráculo e a
  reavaliação.

**Regra que sai disso:** mudança de infraestrutura que vale para todo projeto
do Igor vai para o **playbook**, não para cá. Só o que é específico deste repo
mora em `.claude/` local. Está escrito no `CLAUDE.md`.

Consequências estruturais:

- `ROADMAP.md` saiu da raiz e virou **`docs/ROADMAP.md`**, que é onde o canon
  procura, com um campo **`verificar:`** checável por fatia (o `/tchau` usa ele
  para decidir se avança o ponteiro).
- **`docs/PROXIMO.md`** passa a ser o ponteiro de UMA fatia. Os nomes das
  chaves não foram inventados: saíram do consumidor real, o parser em
  `.claude/hooks/sessao-abre.ps1` (`perfil`, `modelo`, `esforco`, `chat`,
  `titulo`, `forma`, `maquina`, `plan-mode`, `objetivo`) mais `verificar:`, que
  o `/tchau` lê. Os templates oficiais vivem no playbook e **não estão neste
  repo** — se divergirem, o playbook manda.
- **`docs/DESVIOS.md`** criado, sem nenhuma linha (não houve desvio).

**Não é preciso rodar o `/360` para formatar isto.** A análise 360 e o desenho
das fatias já foram feitos à mão nesta sessão; o `/360` serve para *refazer* o
roadmap, e o próprio comando avisa que refazer um roadmap bom é queimar
opus/max para chegar no mesmo lugar.

## C7 — PyMC-Marketing promovido do backlog

`d63afc9`. Continua **pós-publicação** e `blocked` atrás do C6, mas agora está
escrito com a armadilha que ninguém deve redescobrir: **o PyMC-Marketing usa
saturação logística por padrão, não Hill**. O gerador usa Hill exatamente
porque Hill é a interseção das famílias do Meridian e do Robyn (PLAN D3) — e
não é a default do PyMC. Rodar no default mediria o descasamento de forma
funcional, não a ferramenta. A escolha (configurar Hill e declarar, ou tratar o
logístico como cenário separado) tem de ser pré-registrada num
`runs/pymc/DECISIONS.md` **antes** do primeiro run.

O motivo de fazer o C7 mudou: a metade *defensiva* ("três ferramentas erraram,
logo não é bug meu") foi absorvida pelo oráculo, que prova a mesma coisa melhor.
O que sobra é a pergunta aberta — Meridian ancora no prior de ROI, Robyn no
spend share, e um terceiro ancora em quê?

## Próximo passo imediato

- **Karen (esta máquina):** **C1** — a escalada do Robyn.
  `wsl -d Ubuntu -u igor --cd /mnt/c/<repo> -- Rscript runs/robyn/run_robyn.R --iterations=4000 102 103 104`
  (~20 min/seed, CPU, desatendido). Nunca passar `quiet` (fricção F8).
- **Qualquer máquina, em paralelo:** **C2** — piso de sinal/ruído por canal no
  `simulation/checks.py`.
- Detalhe, definition of done e estimativa de cada um: `docs/ROADMAP.md`.

## Pendências

- **C1 fechado** (09/09, sessão retomada). Os cinco extratos do Robyn seguem
  specs documentados (101 e 102-104 a 4000×5, 105 a 2000×5 por já ter
  convergido) — não é mais um "misto" não explicado, é um resultado
  registrado em `runs/robyn/DECISIONS.md`. **3 dos 5 seeds do Robyn continuam
  não convergidos** mesmo a 4000×5 — isso não muda até a peça, só fica mais
  bem documentado. `ORACLE.md` e `REASSESSMENT` citam a cifra antiga (~20%
  cobertura); atualizar para 16% quando qualquer um dos dois for revisado de
  novo (não é bloqueante — só desatualizado).
- **C2** o gate de recuperabilidade.
- **C3–C6** scoring + gráficos, artigo, README público, auditoria final.
- **Subagente e skill só carregam no próximo start da sessão.** Hooks e
  `settings.json` recarregam na hora (verificado). `publication-auditor` e
  `/score` já apareceram no fim desta sessão, então estão ativos.
- **A detecção de máquina por GPU vai pedir permissão uma vez por sessão.** A
  regra `PowerShell(...)` foi tirada do `allow` por não ter sido possível
  verificá-la; o hook `SessionStart` do canon injeta o estado do repositório
  mas **não** detecta a GPU, então o passo continua sendo do `/oi`.
- **`verificar:` do C1 corrigido:** a contagem de iterações fica em
  `run.convergence_detail.iterations`, não em `extras`. A primeira versão do
  campo apontava para o lugar errado e foi consertada antes de qualquer uso.

## Preso a esta máquina (Karen)

- Ambientes WSL2 (Meridian GPU, Robyn multi-core) — reproduzíveis do zero em
  outra máquina com admin via `envs/*.sh` (ordem no topo de `ENVIRONMENT.md`).
- Outputs pesados (gitignored, ~1,2 GB): `outputs/meridian/*.pkl`,
  `outputs/robyn/seed*/OutputModels.rds|OutputCollect.rds`.
- **C1 só roda aqui** (precisa do R no WSL2). C2 em diante roda em qualquer
  máquina — Python puro sobre arquivos commitados.

## Fricções anteriores que continuam valendo

- `robyn_run(quiet=TRUE)` crasha no 3.12.1 (`object 'pb' not found`) — nunca
  passar `quiet` (F8, `envs/ENVIRONMENT.md`).
- Geo do Meridian não convergiu a 500/500 nem 1000/1000; 2000/2000 resolveu
  para seed102 e quase para seed101 — três tentativas documentadas, sem quarta.
- Reconstrução de curva do Robyn: pegar o elemento certo do retorno de
  `saturation_hill`; o self-check em m=1 vs `xDecompAgg` pega o erro na hora.
