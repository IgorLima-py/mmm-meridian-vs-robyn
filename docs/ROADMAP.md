# Roadmap

Quatro blocos e o quinto, de decisões. Quem escreve é o `/360` (este, de 27/09/2026); quem lê é
o `/tchau` (para resolver o perfil da próxima fatia), o hook de abertura e o Igor.

A v1 (C0–C8) está publicada, e o roadmap dela fica arquivado sem mudança em
`docs/ROADMAP_V1.md`. É lá que mora a spec da C7 (PyMC-Marketing), herdada pela C19c. O `C9b`
do `git log` é fatia do playbook, não deste roadmap. A v2 sai em duas entregas: a **parte 2**
(C10–C14), curta, sobre os dados da v1, e a **parte 3** (C16–C22), com calibração por
experimento, PyMC-Marketing e gasto endógeno. Entre as duas fica a C15, a ferramenta de
recuperabilidade. A C23 é a página.

---

## 1. Tabela de perfis

A política num lugar só — mudar política é **uma** edição, não N. Cada fatia aponta para um
perfil; nenhuma fatia escreve modelo e esforço direto.

| Perfil | Modelo | Esforço | Quando |
|---|---|---|---|
| `leve`    | haiku  | low    | ler, resumir, exportar |
| `ajuste`  | sonnet | low    | corrigir texto, renomear, uma conta só |
| `padrao`  | sonnet | medium | fatia mecânica, tela, worker, chamada de rede, run longo |
| `dificil` | opus   | high   | schema, serviço de fundo, quebrar arquivo, análise nova |
| `replan`  | opus   | xhigh  | replanejar, pesquisar frente nova, decidir escopo, pré-registrar |
| `publicacao` | opus | xhigh | escrever e auditar texto que vai a público (escolha do Igor, 27/09; a v1 usou opus/max na C4 e na C6) |

**Regra de correção:** consertar o que uma fatia entregou errado usa **o modelo daquela fatia e
um nível de esforço acima**. Quem errou não foi o modelo, foi o orçamento de pensar.

---

## 2. A fila

Estado: ✅ feito · 🚧 em obras · ⬜ não começou · 🔴 travado

| # | Chat | Perfil | Forma | Estado | Máquina | Depende de | Paralelo com | O que muda no dia seguinte |
|---|---|---|---|---|---|---|---|---|
| 1 | C10 — Quanto do erro da v1 era setup | `dificil` | sessao | ⬜ | qualquer | — | — | dá para dizer, por canal e por ferramenta, quanto do erro da v1 era setup e quanto era ferramenta: a pergunta que o `analysis/AUDIT.md` deixou aberta |
| 2 | C11 — Regret de orçamento com otimizador neutro | `dificil` | sessao | ⬜ | qualquer | C10 | — | dá para dizer quanto do incremental possível cada ferramenta perde numa realocação; existe validador de schema para todo JSON de resultado |
| 3 | C12 — Alocadores das ferramentas nos modelos da v1 | `padrao` | sessao | ⬜ | Karen | C11 | — | dá para comparar o que o alocador de cada ferramenta recomenda com o ótimo verdadeiro, limitação que a v1 declarou |
| 4 | C13 — Parte 2 escrita | `publicacao` | sessao | ⬜ | qualquer | C10, C11, C12 | — | o Igor lê a parte 2 inteira, com números que se auto-conferem, e decide se ela vai para o auditor como está |
| 5 | C14 — Auditoria e publicação da parte 2 | `publicacao` | sessao | ⬜ | qualquer | C13 | — | a parte 2 está pública e o README abre por ela |
| 6 | C15 — Checagem de recuperabilidade reutilizável | `dificil` | sessao | ⬜ | qualquer | — | — | qualquer pessoa roda a checagem antes de confiar num MMM; a parte 3 ganha o portão por canal |
| 7 | C16 — Ambientes e piloto da parte 3 na Karen | `padrao` | sessao | ⬜ | Karen | — | — | a Karen roda Meridian 2.x, PyMC-Marketing e Robyn travado, e o pré-registro tem tempos medidos e a spec do Robyn que converge |
| 8 | C17 — Pré-registro da parte 3 | `replan` | sessao | ⬜ | qualquer | C15, C16 | — | o desenho da parte 3 fica travado em commit antes de qualquer run |
| 9 | C18 — Simulador da parte 3 | `dificil` | sessao | ⬜ | qualquer | C17 | — | existem os dados dos dois cenários, com e sem os cinco experimentos, e os lifts estimados |
| 10 | C19a — Runs do Meridian 2.x | `padrao` | sessao | ⬜ | Karen | C16, C18 | — | existem os 90 extratos do Meridian |
| 11 | C19b — Runs do Robyn calibrado | `padrao` | sessao | ⬜ | Karen | C16, C18 | — | existem os 90 extratos do Robyn |
| 12 | C19c — Runs do PyMC-Marketing | `padrao` | sessao | ⬜ | Karen | C16, C18 | — | existem os 90 extratos do PyMC-Marketing; a C7 da v1 fecha aqui |
| 13 | C20 — Pontuação da parte 3 | `dificil` | sessao | ⬜ | qualquer | C19a, C19b, C19c | — | existem as tabelas pré-registradas: quanto cada experimento compra, por ferramenta e por cenário |
| 14 | C21 — Parte 3 escrita | `publicacao` | sessao | ⬜ | qualquer | C20 | — | o Igor lê a parte 3 inteira, já com o nome novo do repo, e decide se ela vai para o auditor |
| 15 | C22 — Auditoria, rename e publicação da parte 3 | `publicacao` | sessao | ⬜ | qualquer | C21 | — | a parte 3 está pública, com o repo no nome novo |
| 16 | C23 — Página interativa | `padrao` | sessao | ⬜ | Karen | C22 | — | a página está no ar no endereço definitivo |

A última coluna é a que impede fatia decorativa: se nada muda no dia seguinte, a fatia não
merece um chat.

---

## 3. Uma seção por fatia

Valem para todas: a v1 publicada (`article/meridian-vs-robyn.md`) não é tocada; o `README.md`
só muda em fatia de publicação (C14, C15, C22, C23); rascunho público leva `DRAFT` na primeira
linha; "a cadeia do /score" é `python -m simulation.checks`, `python analysis/oracle.py` e
`python analysis/scoring.py --results runs --data data/sim --out analysis/out`, nessa ordem,
todos saindo 0.

### C10 — Quanto do erro da v1 era setup: o oráculo com as restrições de cada ferramenta

`dificil` · opus · high · forma: sessao · máquina: qualquer · plan mode: não · contexto: limpo antes

**persona:** estatístico de simulação que desconfia do próprio oráculo
**entra:** `analysis/AUDIT.md` (seção "What the audit did not resolve"); `analysis/ORACLE.md`;
`analysis/oracle.py`; `runs/meridian/DECISIONS.md`; `runs/robyn/DECISIONS.md` e
`runs/robyn/run_robyn.R` (θ por canal, α 0,5–3, γ 0,3–1); `simulation/config.py`; `docs/PLAN.md`
(emendas de 11/09); `docs/BACKLOG.md` item 8; bloco 5 deste roadmap.
**sai:** (a) emenda datada no `docs/PLAN.md` com o pré-registro da parte 2 inteira — os degraus
novos do oráculo, a métrica de regret e os limites por canal que a C11 e a C12 usam —, num
commit só dela, antes de qualquer número novo; (b) os degraus em `analysis/oracle.py`: o do setup
do Meridian (slope 1, `max_lag=13`) e o do setup do Robyn (θ e γ dentro dos bounds dele),
respondendo as três perguntas abertas do AUDIT; (c) os JSONs em `runs/oracle/results/`; (d) a
seção `## Setup-constrained rungs` no `analysis/ORACLE.md` (inglês); (e) correlação de postos
(ROI estimado × verdadeiro) e dispersão por seed da diferença entre ferramentas no
`analysis/scoring.py`; (f) `docs/BACKLOG.md` item 8 apontando para cá.
**verificar:** (1) `git log --format=%h --reverse -- docs/PLAN.md runs/oracle/results/` mostra o
commit da emenda antes do primeiro commit que traz JSON novo, e são commits diferentes; (2) cada
degrau que a emenda declara tem 5 JSONs (seeds 101–105) em `runs/oracle/results/`; (3) a cadeia
do /score sai 0; (4) rodar `python analysis/oracle.py` de novo deixa
`git diff --ignore-cr-at-eol --exit-code runs/oracle/results/` em 0; (5) a seção
`## Setup-constrained rungs` existe e cita cada degrau novo pelo nome que a emenda deu (um
`grep` por nome dentro da seção).
**prompt de abertura:**

> Você é um estatístico de simulação que desconfia do próprio oráculo. Esta é a C10 do
> mmm-meridian-vs-robyn, a primeira fatia da parte 2: responder, nos dados da v1 e sem rodar
> ferramenta nenhuma, quanto do erro de cada ferramenta vinha do setup. Leia o que a seção da
> C10 no `docs/ROADMAP.md` lista em **entra**. Primeiro escreva e commite, sozinha, a emenda de
> pré-registro da parte 2 no `docs/PLAN.md` (degraus, regret, limites por canal): nenhum número
> novo antes desse commit. Depois implemente os degraus, rode a cadeia do /score e escreva a
> seção no `ORACLE.md`. Pronto é o **verificar** da C10, item por item.

### C11 — O erro custa dinheiro? Regret de orçamento com otimizador neutro

`dificil` · opus · high · forma: sessao · máquina: qualquer · plan mode: não · contexto: limpo antes

**persona:** analista de alocação de orçamento, cético com métrica de ROI que não vira decisão
**entra:** a emenda da C10 no `docs/PLAN.md`; `analysis/RESULTS_SCHEMA.md` (campo
`response_curve`); `analysis/scoring.py`; `runs/*/results/*.json`; `data/sim/seed*/ground_truth.json`.
**sai:** `analysis/regret.py` — otimizador neutro (orçamento total fixo; limites por canal da
emenda num `BOUNDS` com a origem comentada; curvas interpoladas na grade do gerador) — com
`--selftest`; `analysis/validate_schema.py` com `--strict` (sai ≠ 0 em arquivo fora do
`RESULTS_SCHEMA.md`, inclusive pulado em silêncio) e `--allocations` (confere os limites de cada
JSON de alocação contra o `BOUNDS`); a tabela `## Budget regret` no `analysis/out/summary.md`,
uma linha por estimador.
**verificar:** (1) `python analysis/regret.py --selftest` sai 0, e
`grep -c "def test_true_curves_zero_regret\|def test_perturbed_curve" analysis/regret.py` = 2
(curvas verdadeiras dão regret 0 a 1e-9; curva perturbada à mão dá o valor calculado no teste);
(2) `python analysis/validate_schema.py --strict runs/*/results/*.json` sai 0 sobre os extratos
da v1; (3) a cadeia do /score sai 0; (4) `analysis/out/summary.md` tem `## Budget regret` com as
linhas Meridian, Robyn e oracle.
**prompt de abertura:**

> Você é um analista de alocação de orçamento, cético com métrica de ROI que não vira decisão.
> C11 do mmm-meridian-vs-robyn: com as curvas que os extratos da v1 já trazem, medir quanto do
> incremental possível cada ferramenta perde numa realocação, com um otimizador neutro e os
> limites que a emenda da C10 pré-registrou. Leia o **entra** da C11 no `docs/ROADMAP.md`.
> Escreva também o validador de schema: ele serve às fatias C12 e C16 a C20. Pronto é o
> **verificar** da C11.

### C12 — O que os alocadores das ferramentas recomendam, contra o ótimo verdadeiro

`padrao` · sonnet · medium · forma: sessao · máquina: Karen · plan mode: não · contexto: limpo antes

**persona:** engenheiro de ML que conhece o Robyn e o Meridian por dentro
**entra:** a emenda da C10 (limites por canal); `analysis/regret.py` (`BOUNDS`);
`runs/meridian/run_meridian.py`; `runs/robyn/run_robyn.R`; `envs/ENVIRONMENT.md` (venvs da WSL2;
nunca `quiet=TRUE` no Robyn; `bash -lc "cd ... && ..."` em vez de `wsl --cd` em segundo plano); os
modelos salvos em `outputs/meridian/*.pkl` e `outputs/robyn/seed*/OutputCollect.rds` (só na Karen).
**sai:** scripts que rodam `robyn_allocator()` e o `BudgetOptimizer` do Meridian 1.8.0 sobre os
modelos já ajustados, sem refit, com os limites do `BOUNDS`; 10 JSONs de alocação (braço
nacional, 5 seeds × 2 ferramentas) em `runs/*/results/`, com o formato documentado no
`analysis/RESULTS_SCHEMA.md`; regret do alocador próprio no summary; entrada datada no
`DECISIONS.md` de cada ferramenta (inclusive que o Robyn da seed 105 é 2000×5 e as outras 4000×5).
**verificar:** (1) `ls runs/meridian/results runs/robyn/results | grep -c allocation` = 10;
(2) `python analysis/validate_schema.py --strict --allocations runs/*/results/*allocation*.json`
sai 0; (3) a cadeia do /score sai 0 e a tabela `## Budget regret` ganha as linhas do alocador
próprio das duas ferramentas.
**prompt de abertura:**

> Você é um engenheiro de ML que conhece o Robyn e o Meridian por dentro, na Karen. C12 do
> mmm-meridian-vs-robyn: rodar o alocador de cada ferramenta sobre os modelos da v1 já salvos em
> `outputs/`, sem refit, com os limites do `BOUNDS` da C11, e exportar a alocação recomendada.
> Leia o **entra** da C12 no `docs/ROADMAP.md`, e as pegadinhas de WSL2 do `ENVIRONMENT.md`
> antes do primeiro comando. Pronto é o **verificar** da C12.

### C13 — Parte 2 escrita: artigo curto, figuras e o README-índice em rascunho

`publicacao` · opus · xhigh · forma: sessao · máquina: qualquer · plan mode: não · contexto: limpo antes

**persona:** redator técnico que escreve para quem decide orçamento, sem inflar número
**entra:** `analysis/ORACLE.md` (seção nova); `analysis/out/summary.md`; `analysis/figures.py`
(`roi_facts` e `curve_facts` como modelo); o artigo da v1 e o `README.md` (só leitura);
`CLAUDE.md` (frase proibida, sem vencedor, seção obrigatória); skills `dataviz` e `humanize`.
**sai:** `article/part-2.md` (inglês, ≤ 1.000 palavras — a meta de artigo curto que a C4 da v1
tinha —, primeira linha `DRAFT`), com a seção "What neither tool can tell you"; figuras novas por
`analysis/figures.py`, com uma função `part2_*_facts()` que afirma cada número das legendas;
`docs/drafts/README-part2.md` — o README como índice (parte 2 no topo, parte 1 abaixo), com a
frase de reprodutibilidade corrigida (ruído no 16º dígito entre máquinas, `docs/STATUS.md` de
24/09); a saída do conferidor da `humanize` para os dois arquivos, registrada na seção da C13 do
`docs/STATUS.md`.
**verificar:** (1) `wc -w article/part-2.md` ≤ 1000; (2) `python analysis/figures.py` sai 0 e
`grep -c "def part2_.*facts" analysis/figures.py` ≥ 1; (3) a seção da C13 no `docs/STATUS.md`
traz a linha `nada novo` do conferidor para os dois arquivos; (4) `head -1 article/part-2.md` é
`DRAFT`; (5) `docs/drafts/README-part2.md` cita `article/meridian-vs-robyn.md` e
`article/part-2.md` (um `grep` por nome); (6)
`grep -niE "came back identical|byte-for-byte identical" docs/drafts/README-part2.md` não devolve
nada; (7) `README.md` e `article/meridian-vs-robyn.md` não ganharam commit nesta fatia.
**prompt de abertura:**

> Você é um redator técnico que escreve para quem decide orçamento, sem inflar número. C13 do
> mmm-meridian-vs-robyn: escrever a parte 2 ("o que a v1 deixou aberto"), com no máximo 1.000
> palavras, a partir do que a C10, a C11 e a C12 mediram. O README novo nasce como rascunho em
> `docs/drafts/`; o `README.md` e o artigo da v1 não mudam. Leia o **entra** da C13 no
> `docs/ROADMAP.md` e as regras do `CLAUDE.md`: frase proibida, sem vencedor, a seção
> "What neither tool can tell you". Pronto é o **verificar** da C13.

### C14 — Auditoria da parte 2 até SHIP, e publicação

`publicacao` · opus · xhigh · forma: sessao · máquina: qualquer · plan mode: não · contexto: limpo antes

**persona:** editor que só publica o que passou pelo auditor
**entra:** `.claude/agents/publication-auditor.md`; `analysis/AUDIT.md`; `article/part-2.md`;
`docs/drafts/README-part2.md`; `analysis/ORACLE.md` e `analysis/out/summary.md`; `docs/STATUS.md`
(o auditor em escopo largo estourou 40 turnos na C3, na C4 e na C6: uma rodada por artefato).
**sai:** rodadas do `publication-auditor`, uma por artefato, até SHIP; bloco `## Part 2 audit`
no fim do `analysis/AUDIT.md`, com subtítulos `###`; `README.md` trocado pelo rascunho auditado e
`docs/drafts/README-part2.md` removido; a linha `DRAFT` fora do artigo; tag `part-2` (push da tag
só com o OK do Igor); o About do GitHub revisto pelo Igor, que é quem aplica.
**verificar:** (1) o bloco sob `## Part 2 audit` (até o próximo `## ` ou o fim) termina em
`VERDICT: SHIP`; (2) `grep -c DRAFT article/part-2.md` = 0; (3) um clone limpo num caminho curto
(`%TEMP%\mmc`) roda a camada 1 do README, com os comandos da parte 2, e sai 0; (4)
`git ls-remote --tags origin part-2` devolve a tag; (5) `docs/drafts/README-part2.md` não existe
mais e o `README.md` cita `article/part-2.md`.
**prompt de abertura:**

> Você é um editor que só publica o que passou pelo auditor. C14 do mmm-meridian-vs-robyn:
> rodar o `publication-auditor` sobre a parte 2, um artefato por rodada, até SHIP, e só então
> trocar o README e tirar o DRAFT. Leia o **entra** da C14 no `docs/ROADMAP.md`. Tag e push da
> tag, só com o OK do Igor. Pronto é o **verificar** da C14.

### C15 — A checagem de recuperabilidade como ferramenta reutilizável

`dificil` · opus · high · forma: sessao · máquina: qualquer · plan mode: não · contexto: limpo antes

**persona:** autor de ferramenta pequena para outros analistas, que só confia em exemplo que roda
**entra:** `analysis/ORACLE.md` ("The reusable part"); `simulation/checks.py` (`channel_snr`);
`simulation/core.py`; `simulation/config.py`; `analysis/oracle.py`; `docs/BACKLOG.md` item 4
(quebra por veículo).
**sai:** pacote `recoverability/` com a CLI `python -m recoverability`: recebe uma config no
formato do `simulation/config.py`, simula, roda o oráculo e imprime, por canal, o S/N e o
veredito recuperável ou não, com o critério e a origem dele escritos; exemplo `v1` (os 5 canais)
e exemplo `social-split` (social partido em 3 veículos com ROIs diferentes, com config própria);
`--selftest`, que confere o exemplo `v1` contra o `ORACLE.md`; `recoverability/README.md`
(inglês), auditado; uma linha no `README.md` apontando a ferramenta. É fatia de publicação da
ferramenta.
**verificar:** (1) `python -m recoverability --selftest` sai 0 (o exemplo `v1` marca tv, search
e social como recuperáveis e ooh e display não, como no `ORACLE.md`); (2)
`python -m recoverability --example social-split` sai 0 e imprime uma linha por veículo; (3) o
bloco `## Recoverability tool audit` do `analysis/AUDIT.md` termina em `VERDICT: SHIP`.
**prompt de abertura:**

> Você é autor de ferramenta pequena para outros analistas, e só confia em exemplo que roda. C15
> do mmm-meridian-vs-robyn: transformar a checagem de recuperabilidade — o conselho do artigo da
> v1 — numa ferramenta que qualquer um roda nos próprios pressupostos antes de confiar num MMM.
> Leia o **entra** da C15 no `docs/ROADMAP.md`. O exemplo de social partido por veículo roda só
> o oráculo, nunca uma ferramenta. Pronto é o **verificar** da C15.

### C16 — Ambientes e piloto da parte 3 na Karen

`padrao` · sonnet · medium · forma: sessao · máquina: Karen · plan mode: não · contexto: limpo antes

**persona:** engenheiro de ambiente que trava versão e mede tempo
**entra:** `envs/` inteiro e `envs/ENVIRONMENT.md`; `docs/BACKLOG.md` item 7 (travar o R);
`docs/STATUS.md` (pegadinhas de WSL2 e do Robyn); `runs/robyn/DECISIONS.md` (as escalações da
v1); `analysis/validate_schema.py`; o bloco 5 deste roadmap.
**sai:** `envs/setup_meridian2.sh` (venv novo; o da 1.8.0 fica, para a v1 seguir reproduzível),
`envs/setup_pymc.sh`, e `envs/setup_robyn.sh` com `remotes::install_version("Robyn", "3.12.1")`
e o nevergrad instalado do lock; cada script imprime a versão instalada; locks commitados; um
smoke por ferramenta (seed 101 da v1, cadeia curta) com o JSON salvo; o tempo por seed do
PyMC-Marketing e do Meridian 2.x no formato "Smoke-test wall-clocks" do `ENVIRONMENT.md`; o
**piloto de convergência do Robyn**: as seeds 102–104 da v1 numa ou mais specs candidatas, que
registra **só** convergência e tempo, nunca erro contra a verdade (senão vira ajuste depois de
ver resultado); `docs/BACKLOG.md` item 7 apontando para cá.
**verificar:** (1) cada `envs/setup_*.sh` roda duas vezes seguidas na WSL2, sai 0 nas duas, e a
versão que imprime é a travada; (2) `python analysis/validate_schema.py --strict` nos 3 JSONs de
smoke sai 0; (3) `git status --porcelain envs/` vazio depois do commit; (4)
`grep -nE "(PyMC|Meridian 2).*[0-9.]+ *(s|min)" envs/ENVIRONMENT.md` acha os dois tempos
medidos; (5) `runs/robyn/DECISIONS.md` tem a tabela do piloto (spec × seed × convergiu × tempo),
sem coluna de erro.
**prompt de abertura:**

> Você é um engenheiro de ambiente que trava versão e mede tempo, na Karen. C16 do
> mmm-meridian-vs-robyn: montar os ambientes da parte 3 (Meridian 2.x num venv novo,
> PyMC-Marketing, Robyn 3.12.1 travado de verdade) e medir o que o pré-registro precisa: tempo
> por seed de cada ferramenta e uma spec do Robyn que converge nas seeds em que a v1 falhou. O
> piloto registra só convergência e tempo. Leia o **entra** da C16 no `docs/ROADMAP.md`. Pronto
> é o **verificar** da C16.

### C17 — Pré-registro da parte 3

`replan` · opus · xhigh · forma: sessao · máquina: qualquer · plan mode: sim · contexto: limpo antes

**persona:** pesquisador que pré-registra antes de olhar e tenta derrubar o próprio desenho
**entra:** o bloco 5 deste roadmap; `docs/PLAN.md`; `docs/ROADMAP_V1.md` (spec da C7); a seção
"Avaliação da v1" do `docs/STATUS.md`; `docs/REASSESSMENT_2026-09-08.md` §2 e §4;
`docs/REFERENCES.md`; `runs/*/DECISIONS.md` (inclusive o piloto da C16);
`envs/ENVIRONMENT.md` (tempos da C16); `analysis/RESULTS_SCHEMA.md`; o benchmark do Heusch
(arXiv 2608.21130: artigo, repositório e licença); a documentação de calibração do Meridian 2.x
(`CalibrationBuilder`, priors de ROI), do Robyn (`calibration_input`, objetivo `MAPE.LIFT`) e do
PyMC-Marketing (`add_lift_test_measurements`); a calculadora geo-holdout do experiment-calculators
(pública, MIT).
**sai:** `docs/PLAN_PART3.md` (inglês) com sete seções:
- **Scenarios:** base = config da v1; endógeno = o do Heusch ou a extensão do nosso, com a
  decisão (`adopted` ou `not adopted`), o identificador da licença e o porquê.
- **Experiments:** holdout geo nos cinco canais, em semanas diferentes, dentro da janela; o DiD e
  o erro-padrão; o tamanho do teste, saído da calculadora, com link.
- **Arms:** sem experimento, o padrão (o setup da v1, que deixa a v1 servir de ponte de versão)
  e o melhor caso; com os experimentos embutidos, o controle sem calibrar e os 6 calibrados
  sobre o padrão. São 9 braços por cenário, e o **N = 90** por ferramenta fica escrito como número.
- **Versions:** Meridian 2.x, PyMC-Marketing 1.x e Robyn 3.12.1, com a spec que o piloto da C16
  achou e a regra de escalação se não convergir. O padrão do PyMC-Marketing é o quickstart da
  versão travada.
- **Metrics:** erro de ROI, cobertura, regret neutro e do alocador próprio, efeito da calibração;
  os títulos exatos das tabelas que a C20 vai emitir.
- **Compute budget:** a partir dos tempos medidos.
- **Prior work:** PyMC Labs 2025, mmm-recovery-bench 2026 e Heusch 2026, com o que cada um mediu,
  o que falta, e o que a v1 errou.

Também saem `docs/REFERENCES.md` e `docs/BACKLOG.md` atualizados.
**verificar:** (1) `grep -c "^## " docs/PLAN_PART3.md` ≥ 7 e os sete títulos acima aparecem; (2)
`grep -A8 "2608.21130" docs/PLAN_PART3.md | grep -qiE "adopted"` e o mesmo bloco traz o
identificador da licença (ex.: `MIT`, `CC-BY-4.0`) — "unknown" não passa; (3)
`git log --oneline -- 'runs/*/results/part3'` vazio (nada rodou antes do pré-registro); (4)
`grep -nE "N = [0-9]+" docs/PLAN_PART3.md` acha o N.
**prompt de abertura:**

> Você é um pesquisador que pré-registra antes de olhar e tenta derrubar o próprio desenho. C17
> do mmm-meridian-vs-robyn: escrever o `docs/PLAN_PART3.md` que trava a parte 3 (calibração por
> experimento, PyMC-Marketing e gasto endógeno) antes de qualquer run. Comece avaliando o
> benchmark do Heusch (arXiv 2608.21130): licença, formato, e se publica os parâmetros
> verdadeiros, sem os quais o oráculo não roda. Leia o **entra** da C17 e o bloco 5 do
> `docs/ROADMAP.md`: o que está lá como `respondida` não se reabre. Pronto é o **verificar** da C17.

### C18 — Simulador da parte 3: gasto endógeno, experimentos nos cinco canais e o estimador de lift

`dificil` · opus · high · forma: sessao · máquina: qualquer · plan mode: não · contexto: limpo antes

**persona:** engenheiro de simulação causal
**entra:** `docs/PLAN_PART3.md`; `simulation/` inteiro; `recoverability/` (vira o portão por
canal); `analysis/RESULTS_SCHEMA.md`; `analysis/validate_schema.py`; o gerador do Heusch, se o
PLAN_PART3 o adotou.
**sai:** o gerador da parte 3, em versão nova, sem mexer no da v1, gravando em
`data/sim_part3/<cenário>/<exp|noexp>/seed<NNN>/`. **Ramo explícito:** se o PLAN_PART3 adotou o
Heusch, o cenário endógeno vem do gerador dele, com os holdouts implementados sobre ele; se não
adotou, vem da extensão do nosso, com citação. Em qualquer ramo: os dois cenários, com e sem os
cinco experimentos embutidos (lift verdadeiro gravado); `analysis/lift.py` (DiD com erro-padrão)
com `--selftest`; os lifts estimados convertidos para a entrada de cada ferramenta; o portão de
recuperabilidade por canal no `simulation/checks.py`; o `RESULTS_SCHEMA.md` e o
`validate_schema.py` com o campo `scenario` e o nome `<tool>_<scenario>_<arm>_seed<NNN>.json`.
**verificar:** (1) `python -m simulation.generate --part3` e `python -m simulation.checks --part3`
saem 0, e `find data/sim_part3 -name ground_truth.json | wc -l` = 20 (2 cenários × com/sem
experimento × 5 seeds); (2) `python analysis/lift.py --selftest` sai 0: sem ruído, recupera o
lift verdadeiro a 1e-9; com ruído, a cobertura do IC de 90% em 200 réplicas fica em
[0,836; 0,964] — ±3 desvios-padrão de uma binomial com n = 200 e p = 0,9; com ±2, um estimador
correto falharia por azar em 1 de 20 seeds de teste; (3) `python -m simulation.generate` (v1) e
depois `git diff --ignore-cr-at-eol --exit-code data/sim/` saem 0 — a v1 não mudou; (4)
`python analysis/validate_schema.py --selftest` sai 0 cobrindo o campo `scenario`.
**prompt de abertura:**

> Você é um engenheiro de simulação causal. C18 do mmm-meridian-vs-robyn: gerar os dados da
> parte 3 exatamente como o `docs/PLAN_PART3.md` pré-registrou — dois cenários, com e sem os
> cinco experimentos de holdout geo — e o estimador DiD do lift. Siga o ramo (Heusch ou o nosso)
> que o PLAN_PART3 escolheu. A v1 não pode mudar um byte. Leia o **entra** da C18 no
> `docs/ROADMAP.md`. Pronto é o **verificar** da C18.

### C19a — Runs do Meridian 2.x

`padrao` · sonnet · medium · forma: sessao · máquina: Karen · plan mode: não · contexto: limpo antes

**persona:** operador de run longo, que registra tudo e não mexe no setup
**entra:** `docs/PLAN_PART3.md` (Arms, Versions, N); `runs/meridian/run_meridian.py` (base da
v1); `data/sim_part3/` e os lifts da C18; o venv da C16; `envs/ENVIRONMENT.md`.
**sai:** `runs/meridian/run_meridian_part3.py`; os 90 JSONs em `runs/meridian/results/part3/`,
cada um com a alocação recomendada pelo `BudgetOptimizer` sob os limites pré-registrados;
`runs/meridian/DECISIONS.md` com cada escalação. Runs lançados destacados na WSL2 (`bash -lc`);
se a sessão fechar com run em curso, o `docs/STATUS.md` diz qual e onde parou.
**verificar:** (1) `ls runs/meridian/results/part3/*.json | wc -l` = o N do `PLAN_PART3.md`
(90); (2) `python analysis/validate_schema.py --strict runs/meridian/results/part3/` sai 0 —
exige `run.converged` booleano e `run.convergence_detail` não vazio em todos.
**prompt de abertura:**

> Você é um operador de run longo, que registra tudo e não mexe no setup. C19a do
> mmm-meridian-vs-robyn, na Karen: rodar os 90 ajustes do Meridian 2.x que o
> `docs/PLAN_PART3.md` lista, destacados na WSL2, exportando o extrato e a alocação de cada um.
> Escalação só pela regra pré-registrada, registrada no `DECISIONS.md`. Leia o **entra** da C19a
> no `docs/ROADMAP.md`. Pronto é o **verificar** da C19a.

### C19b — Runs do Robyn com calibration_input

`padrao` · sonnet · medium · forma: sessao · máquina: Karen · plan mode: não · contexto: limpo antes

**persona:** operador de run longo, que registra tudo e não mexe no setup
**entra:** `docs/PLAN_PART3.md` (Arms, Versions, N, a spec do piloto); `runs/robyn/run_robyn.R`
(base da v1); `data/sim_part3/` e os lifts da C18 no formato `calibration_input`; o R travado da
C16; `envs/ENVIRONMENT.md` (nunca `quiet=TRUE`).
**sai:** `runs/robyn/run_robyn_part3.R`; os 90 JSONs em `runs/robyn/results/part3/`, cada um com
a alocação do `robyn_allocator()` sob os limites pré-registrados; `runs/robyn/DECISIONS.md` com
cada escalação; runs destacados, com o `STATUS.md` dizendo onde parou se a sessão fechar antes.
**verificar:** (1) `ls runs/robyn/results/part3/*.json | wc -l` = o N do `PLAN_PART3.md` (90);
(2) `python analysis/validate_schema.py --strict runs/robyn/results/part3/` sai 0.
**prompt de abertura:**

> Você é um operador de run longo, que registra tudo e não mexe no setup. C19b do
> mmm-meridian-vs-robyn, na Karen: rodar os 90 ajustes do Robyn que o `docs/PLAN_PART3.md`
> lista, com os lifts no `calibration_input` onde o braço pede, destacados na WSL2. Leia o
> **entra** da C19b no `docs/ROADMAP.md`. Pronto é o **verificar** da C19b.

### C19c — Runs do PyMC-Marketing (fecha a C7 da v1)

`padrao` · sonnet · medium · forma: sessao · máquina: Karen · plan mode: não · contexto: limpo antes

**persona:** operador de run longo, que registra tudo e não mexe no setup
**entra:** `docs/PLAN_PART3.md`; a spec da C7 em `docs/ROADMAP_V1.md` (a armadilha logística ×
Hill); `data/sim_part3/` e os lifts da C18 no formato `add_lift_test_measurements`; o venv da C16.
**sai:** `runs/pymc/DECISIONS.md` com a entrada datada **antes** do primeiro run (braço padrão =
quickstart da versão travada, com saturação logística; melhor caso = Hill com priors que contêm a
verdade); `runs/pymc/run_pymc_part3.py`; os 90 JSONs em `runs/pymc/results/part3/`, com a
alocação do `BudgetOptimizer`.
**verificar:** (1) `ls runs/pymc/results/part3/*.json | wc -l` = o N do `PLAN_PART3.md` (90);
(2) `python analysis/validate_schema.py --strict runs/pymc/results/part3/` sai 0; (3)
`git log --reverse --format=%h -- runs/pymc/DECISIONS.md runs/pymc/results/part3/` mostra o
commit do DECISIONS antes do primeiro JSON.
**prompt de abertura:**

> Você é um operador de run longo, que registra tudo e não mexe no setup. C19c do
> mmm-meridian-vs-robyn, na Karen: o PyMC-Marketing como terceiro estimador, herdando a C7 da v1.
> Antes do primeiro run, commite o `runs/pymc/DECISIONS.md` com os dois braços definidos. Depois
> rode os 90 ajustes do `docs/PLAN_PART3.md`. Leia o **entra** da C19c no `docs/ROADMAP.md`.
> Pronto é o **verificar** da C19c.

### C20 — Pontuação da parte 3

`dificil` · opus · high · forma: sessao · máquina: qualquer · plan mode: não · contexto: limpo antes

**persona:** estatístico do harness, que calcula só o que foi pré-registrado
**entra:** `docs/PLAN_PART3.md` (Metrics, com os títulos das tabelas); `analysis/scoring.py`;
`analysis/regret.py`; `analysis/oracle.py`; `analysis/figures.py`; os 270 JSONs da C19.
**sai:** a flag `--part3` no `simulation/checks.py`, no `analysis/oracle.py`, no
`analysis/scoring.py` e no `analysis/figures.py`, com `--strict` no scoring (sai ≠ 0 se pular
arquivo); o oráculo da parte 3; `analysis/out/summary_part3.md` com as tabelas pré-registradas;
`--check-tables`, que confere os títulos do PLAN_PART3 no summary; figuras da parte 3 com
`part3_*_facts()`; a exceção `!analysis/out/summary_part3.md` no `.gitignore` (mesmo padrão das
três que já existem).
**verificar:** (1) `python -m simulation.checks --part3`, `python analysis/oracle.py --part3` e
`python analysis/scoring.py --results runs --data data/sim_part3 --out analysis/out --part3 --strict`
saem 0; (2) `python analysis/scoring.py --part3 --check-tables` sai 0; (3)
`python analysis/figures.py --part3` sai 0; (4) `git check-ignore analysis/out/summary_part3.md`
não devolve nada e o arquivo está commitado.
**prompt de abertura:**

> Você é o estatístico do harness, e calcula só o que foi pré-registrado. C20 do
> mmm-meridian-vs-robyn: pontuar os 270 extratos da parte 3 exatamente pelas métricas e tabelas
> do `docs/PLAN_PART3.md`. Nenhuma métrica nova sem emenda datada. Leia o **entra** da C20 no
> `docs/ROADMAP.md`. Pronto é o **verificar** da C20.

### C21 — Parte 3 escrita

`publicacao` · opus · xhigh · forma: sessao · máquina: qualquer · plan mode: não · contexto: limpo antes

**persona:** redator técnico que escreve para quem decide orçamento, sem inflar número
**entra:** `analysis/out/summary_part3.md`; `docs/PLAN_PART3.md`; `analysis/figures.py`; os
artigos das partes 1 e 2 (só leitura); `CLAUDE.md`; skills `dataviz` e `humanize`.
**sai:** **primeiro passo:** o Igor escolhe o nome novo do repo, e ele fica registrado no bloco
5, para que todo texto já nasça com a URL certa. Depois: `article/part-3.md` (inglês, ≤ 2.000
palavras — o tamanho da v1, 1.811, com folga para o escopo maior —, primeira linha `DRAFT`), com
a seção "What neither tool can tell you"; figuras com `part3_*_facts()`;
`docs/drafts/README-part3.md` (índice: parte 3 no topo, depois a 2 e a 1, mais a ferramenta da
C15); a saída do conferidor da `humanize`, registrada no `docs/STATUS.md`.
**verificar:** (1) `wc -w article/part-3.md` ≤ 2000; (2) `python analysis/figures.py --part3` sai
0 e `grep -c "def part3_.*facts" analysis/figures.py` ≥ 1; (3) a seção da C21 no
`docs/STATUS.md` traz a linha `nada novo` do conferidor para os dois arquivos; (4)
`head -1 article/part-3.md` é `DRAFT`; (5) `docs/drafts/README-part3.md` cita
`article/meridian-vs-robyn.md`, `article/part-2.md` e `article/part-3.md` (um `grep` por nome);
(6) o bloco 5 tem a linha `respondida` com o nome novo; (7) `README.md` e os dois artigos
publicados não ganharam commit nesta fatia.
**prompt de abertura:**

> Você é um redator técnico que escreve para quem decide orçamento, sem inflar número. C21 do
> mmm-meridian-vs-robyn: antes de escrever, pergunte ao Igor o nome novo do repo e registre-o no
> bloco 5. Depois escreva a parte 3 (≤ 2.000 palavras) a partir do `summary_part3.md`, com o
> README-índice em rascunho em `docs/drafts/`. Leia o **entra** da C21 no `docs/ROADMAP.md`.
> Pronto é o **verificar** da C21.

### C22 — Auditoria da parte 3, rename do repo e publicação

`publicacao` · opus · xhigh · forma: sessao · máquina: qualquer · plan mode: não · contexto: limpo antes

**persona:** editor que só publica o que passou pelo auditor
**entra:** como a C14, com `article/part-3.md`, `docs/drafts/README-part3.md`,
`analysis/out/summary_part3.md` e o nome novo registrado na C21.
**sai:** rodadas do auditor, uma por artefato, até SHIP, no bloco `## Part 3 audit` do
`analysis/AUDIT.md`; README trocado e rascunho removido; `DRAFT` fora do artigo; o rename, feito
pelo Igor ou com o OK dele (`gh repo rename`); os links internos (README, artigos, `CLAUDE.md`,
`envs/`) atualizados; `git remote set-url` nesta máquina, com o passo anotado no `STATUS.md` para
a outra; tag `part-3`; o About do GitHub revisto pelo Igor.
**verificar:** (1) o bloco sob `## Part 3 audit` termina em `VERDICT: SHIP`; (2)
`gh repo view IgorLima-py/<nome-novo> --json name` devolve o nome novo; (3)
`git remote get-url origin` aponta para ele; (4) um clone limpo da URL nova roda a camada 1 do
README e sai 0; (5) `git ls-remote --tags origin part-3` devolve a tag; (6)
`grep -c DRAFT article/part-3.md` = 0.
**prompt de abertura:**

> Você é um editor que só publica o que passou pelo auditor. C22 do mmm-meridian-vs-robyn:
> auditar a parte 3, um artefato por rodada, até SHIP; depois, com o OK do Igor, renomear o
> repo para o nome registrado na C21, atualizar os links e publicar. Leia o **entra** da C22 no
> `docs/ROADMAP.md`. Pronto é o **verificar** da C22.

### C23 — Página interativa no GitHub Pages

`padrao` · sonnet · medium · forma: sessao · máquina: Karen · plan mode: não · contexto: limpo antes

**persona:** designer-engenheiro de visualização de dados
**entra:** `analysis/out/summary*.md` e `summary*.csv`; `runs/*/results/`; os três artigos; o
experiment-calculators como referência de padrão (HTML estático no Pages); a skill `impeccable`
na instalação de usuário da Karen (**não** vendorizar no repo) e a `dataviz`.
**sai:** `site/` em HTML/JS estático, sem build, lendo `site/data/*.json`, gerados por
`analysis/export_site_data.py` a partir dos resultados commitados. A página mostra o erro por
canal e por ferramenta, a escada do oráculo, o regret, e o seletor de experimento (as combinações
que rodaram), com cada ferramenta se mexendo. Também saem: a escala de severidade da auditoria de
UI, definida antes de auditar, e o resultado em `docs/UI_AUDIT.md`; o Pages publicando `site/`; e
o link no `README.md`.
**verificar:** (1) `/run`: a página abre localmente e o seletor de experimento muda os gráficos;
(2) `curl -s https://igorlima-py.github.io/<nome-novo>/ | grep -c 'id="experiment-selector"'`
≥ 1; (3) regerar `site/data/` com `python analysis/export_site_data.py` deixa
`git diff --ignore-cr-at-eol --exit-code site/data/` em 0; (4) a última linha não vazia de
`docs/UI_AUDIT.md` é `UI-VERDICT: PASS`; (5) `git ls-files .claude/skills/impeccable` vazio
(nada vendorizado).
**prompt de abertura:**

> Você é um designer-engenheiro de visualização de dados, na Karen. C23 do mmm-meridian-vs-robyn:
> a página interativa das três partes no GitHub Pages do repo, em HTML/JS estático sem build,
> com todo número vindo de arquivo de dados gerado a partir dos resultados commitados. Use o
> impeccable da instalação de usuário, sem copiá-lo para o repo. Defina a escala de severidade
> da auditoria de UI antes de auditar. Leia o **entra** da C23 no `docs/ROADMAP.md`. Pronto é o
> **verificar** da C23.

O `verificar:` tem dente: o `/tchau` olha para ele antes de avançar o ponteiro, e **não avança**
se faltar item. Ponteiro adiantado é pior que ponteiro parado.

---

## 4. Tabela de escape

Para quando o trabalho **não** é uma fatia, que é a maioria dos dias.

| O que se vai pedir | Perfil |
|---|---|
| mudar texto, cor, tamanho, uma palavra | `ajuste` |
| mudar o comportamento de algo que já funciona | `padrao` |
| um bug que se **consegue** reproduzir | `padrao` |
| um bug que aparece **às vezes** | `dificil` |
| **não sei descrever o problema direito** | `dificil` |

A regra em uma linha: *«às vezes» e «não sei por quê» pedem mais esforço; o resto não.*

---

## 5. Decisões da entrevista

```
2026-09-27 | respondida | Destino da v2 | partes novas neste repo; a v1 publicada fica congelada como registro auditado | nenhuma fatia edita article/meridian-vs-robyn.md
2026-09-27 | respondida | Profundidade da entrevista | Fundo | 6 rodadas
2026-09-27 | respondida | Página de entrada (README) | índice, com a parte mais nova no topo | C13 e C21 fazem o rascunho, C14 e C22 trocam
2026-09-27 | respondida | Configuração das ferramentas | dois braços: padrão (o que um usuário roda) e melhor caso (cada ferramenta capaz de expressar a verdade) | C17 define, C19a-c rodam
2026-09-27 | respondida | Cenário novo | gasto endógeno, no máximo um cenário novo | C17, C18
2026-09-27 | respondida | Visual | página interativa no GitHub Pages deste repo | C23
2026-09-27 | respondida | Entregas | duas: parte 2 curta (análise sobre a v1 + alocadores) e parte 3 completa | C10-C14 e C16-C22
2026-09-27 | respondida | Canais do experimento | os cinco (o Igor: "por que não todos?") | C18
2026-09-27 | respondida | Combinações calibradas | nenhuma, cada canal sozinho, todos | 6 braços calibrados por cenário
2026-09-27 | respondida | Estimador do lift | DiD em Python neste repo; tamanho do teste pela calculadora geo-holdout do experiment-calculators, com link | C18; geo-holdout-testing só citado depois de público
2026-09-27 | respondida | Checagem de recuperabilidade reutilizável | sim, fatia própria | C15
2026-09-27 | respondida | Origem do cenário endógeno | avaliar o benchmark do Heusch (arXiv 2608.21130) primeiro; estender o nosso só se ele não servir | C17 decide, C18 segue o ramo
2026-09-27 | respondida | Base da calibração | em cima do padrão | braços calibrados = padrão + experimento
2026-09-27 | respondida | Nome do repo | renomear na publicação da parte 3 (contra a recomendação de manter) | nome escolhido no começo da C21, rename na C22, página depois
2026-09-27 | respondida | stack travada | Python + R só para o Robyn + WSL2 na Karen + página estática sem build; o Igor aceita deixar o Dell de fora onde precisar de admin | linha stack travada: no CLAUDE.md; coluna Máquina por fatia
2026-09-27 | respondida | Alocadores próprios na parte 2 | sim, fatia curta na Karen sobre os modelos salvos da v1 | C12
2026-09-27 | respondida | Onde a v2 é feita | na main, rascunho com linha DRAFT; README só muda em fatia de publicação | C13 e C21 marcam, C14 e C22 tiram
2026-09-27 | respondida | Quando sai a página | com a parte 3, depois do rename | C23 depois da C22
2026-09-27 | respondida | Dados da parte 3 | os dois conjuntos: padrão e melhor caso sem experimento; controle sem calibrar e os 6 calibrados com os cinco experimentos embutidos | 9 braços por cenário, N = 90 por ferramenta (~11 h de Meridian e ~25 h de Robyn pelos tempos da v1)
2026-09-27 | respondida | impeccable | usar a instalação de usuário da Karen, sem vendorizar | C23 na Karen
2026-09-27 | respondida | Perfil de escrita e auditoria | opus/xhigh, no perfil publicacao | C13, C14, C21, C22
2026-09-27 | assumida   | Versão do Meridian na parte 3 | 2.x em todos os braços da parte 3; priors de ROI já existiam na 1.x, e a v1 (1.8.0) serve de ponte de versão | C16, C17
2026-09-27 | assumida   | O que é o braço padrão | o setup da v1 (defaults + as generosidades documentadas, como max_lag=13), para a v1 servir de ponte sem run extra | C17
2026-09-27 | assumida   | Padrão do PyMC-Marketing | o quickstart oficial da versão travada (saturação logística); melhor caso = Hill com priors que contêm a verdade | C17, C19c
2026-09-27 | assumida   | Seeds | 5, as mesmas da v1 | compute da C19
2026-09-27 | assumida   | Nível do ajuste | nacional; os geos servem de substrato do experimento | C18
2026-09-27 | assumida   | Regret da parte 2 | otimizador neutro sobre as curvas exportadas, com os mesmos limites para os alocadores próprios | C11, C12
2026-09-27 | assumida   | Quebra por veículo | só como exemplo da checagem reutilizável (o oráculo diz se cada veículo é recuperável), sem run de ferramenta | C15
2026-09-27 | assumida   | Frase "every regenerated tracked artifact came back identical" do README | corrigida no README-índice (ruído no 16º dígito entre máquinas, STATUS de 24/09) | C13
2026-09-27 | assumida   | .agents/, .codex/ e AGENTS.md neste repo | fora do git pelo .git/info/exclude, porque a regra do playbook diz que não vão para projeto nenhum; apagar é decisão do Igor | feito na aprovação deste roadmap
2026-09-27 | assumida   | Bateria | continua python -m simulation.checks; as fatias de análise rodam a cadeia do /score no verificar | —
2026-09-27 | assumida   | Auditoria | uma fatia por parte, com o auditor em escopo estreito (um artefato por rodada), porque em escopo largo ele estourou 40 turnos na C3, na C4 e na C6 | C14, C22
2026-09-27 | assumida   | Alocadores próprios na parte 3 | cada run exporta a alocação recomendada sob os limites pré-registrados | C19a-c, C20
2026-09-27 | assumida   | Piloto do Robyn antes do pré-registro | seeds 102-104 da v1 em specs candidatas, registrando só convergência e tempo | C16
2026-09-27 | fora       | GeoLift | o estimador é DiD em Python; GeoLift seria mais uma dependência R sem versão travada | —
2026-09-27 | fora       | Framework JS com build | a página não precisa; estático como o experiment-calculators | —
2026-09-27 | fora       | Quebra por veículo como cenário com run de ferramenta | o gasto endógeno foi o único cenário novo escolhido | —
2026-09-27 | fora       | Todas as 31 combinações | mais de 130 h de Meridian e Robyn | —
2026-09-27 | fora       | geo-holdout-testing como dependência de código | privado, sem artigo, outro gerador de dados | —
2026-09-27 | fora       | Regerar a v1 com a D5 corrigida (BACKLOG 9) | o braço melhor caso resolve pela configuração, sem mudar os dados | —
2026-09-27 | fora       | Braço R&F do Meridian e braço de sensibilidade (BACKLOG 5 e 6) | o braço melhor caso cobre a pergunta do setup | —
2026-09-27 | fora       | Vendorizar o impeccable | 2,2 MB de terceiro (536 KB de JS minificado) no histórico público | —
2026-09-27 | aberta     | Spec do Robyn que converge nas 5 seeds | na v1, nem 4000x5 convergiu em 3 seeds | C16 mede, C17 trava
2026-09-27 | aberta     | Licença e formato do benchmark do Heusch | não conferidos | C17, C18
2026-09-27 | aberta     | O nome novo do repo | o Igor escolhe no começo da C21 | C21, C22, C23
2026-09-27 | aberta     | O GitHub redireciona o endereço antigo do Pages depois do rename? | não conferido | C23, e só importa se alguém linkar a página antes
```
