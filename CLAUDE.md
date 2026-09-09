# mmm-meridian-vs-robyn — instruções permanentes

Comparação dos dois MMMs open-source (Google Meridian e Meta Robyn) sobre o mesmo
dataset simulado com ground truth conhecida. A peça compara ferramentas e explica
limites — ela **não** alega "construí um MMM".

## Regras que valem sempre

- **Este repositório nasceu privado mas VAI ser público — com o histórico inteiro.**
  Todo commit, desde o primeiro, precisa passar no teste: *"isto pode ser lido por
  qualquer pessoa, para sempre?"* Se não pode, não entra.
- **Só dado simulado ou demo público.** Nenhum dado real de anunciante, nenhum dado
  de empregador — atual ou anterior.
- **A frase proibida:** nada aqui — README, código, comentário, mensagem de commit —
  pode dizer ou insinuar "built an MMM" como credencial. O enquadramento é sempre
  comparação e leitura crítica de ferramentas.
- **Sem vencedor absoluto.** A resposta honesta é condicional: qual ferramenta foi
  melhor, sob quais condições. Generalizar "X é melhor" não passa.
- **Reprodutibilidade total:** versões pinadas, seeds fixos, configs commitadas.
  Qualquer pessoa re-roda tudo. É o sinal de credibilidade desta peça.
- **Nenhuma credencial no repo.** Segredos moram em `C:\chaves` / `~/chaves`.
- **Padrão de honestidade:** a seção "What neither tool can tell you" é obrigatória;
  premissas, priors e cada decisão de setup ficam documentadas.
- **Idioma:** artefatos do repo em **inglês**. Conversa com o Igor e docs de sessão
  em português.
- O planejamento mais amplo do portfólio mora em repositório privado separado.
  **Nada de lá é citado ou copiado para cá.**

## O que roda onde

**Local de preferência:** Meridian (Python) e Robyn (R) exigem ambientes pesados e
runs demorados — instalar e rodar na máquina. Escrita e análise dos resultados podem
rodar em qualquer lugar. Documentar no PLAN o setup exato de cada ambiente.

## Duas máquinas

O trabalho alterna entre dois PCs, ambos com o repositório clonado. O handoff
entre eles é **git + `docs/STATUS.md`** — nunca outra coisa:

- **Nunca trocar de máquina sem `/tchau`** (commit + push). Sempre abrir com
  `/oi` (pull). Trabalho não commitado não existe na outra máquina.
- Ambientes (WSL2, venvs Python, biblioteca R) **não viajam pelo git**: os
  scripts de setup em `envs/` devem ser idempotentes, para reproduzir o ambiente
  em qualquer máquina do zero.
- Outputs pesados de model run (pasta ignorada pelo git) ficam na máquina que
  rodou; os **extratos pequenos** em `runs/*/results/` são commitados e viajam.
  O `docs/STATUS.md` registra em qual máquina cada run pesado ficou.
- Runs longos: começar e terminar na mesma máquina. Se um run ficou pela metade,
  anotar no STATUS antes do `/tchau`.
- **Papéis:** a **Karen** (desktop, GPU NVIDIA, admin OK) é a máquina de runs —
  ambientes WSL2 e Fases 1, 3 e 4 do PLAN. O **Dell** (laptop, **sem admin**)
  faz o trabalho sem ferramenta pesada — Fases 2, 5 e 6 (simulador, scoring,
  análise, escrita). A identificação é por GPU no `/oi` (nunca por hostname —
  hostname de máquina não entra em arquivo do repo).

## A primeira sessão — planejamento (antes de qualquer código)

> **Concluída em 2026-08-27** — `docs/PLAN.md`, `docs/REFERENCES.md` e
> `docs/BACKLOG.md` existem. O roteiro abaixo fica como registro.

1. Lê `BRIEF.md` inteiro — ele é o escopo de partida, não o plano.
2. **Pesquisa na internet, a fundo** — a seção "Open questions" do brief é o roteiro:
   versões e docs atuais das duas ferramentas, dores de instalação no Windows,
   datasets demo vs. simulação, literatura de simulação de dados de MMM,
   comparações já publicadas (para diferenciar e citar), runtime esperado.
3. Escreve `docs/PLAN.md` (desenho da simulação, setup de cada ambiente, ordem de
   execução, estimativas) e `docs/REFERENCES.md`.
4. Mostra o plano ao Igor e **só começa a executar depois do OK dele.**

## Ao abrir a sessão

Executado pelo comando `/oi`. **Ele é deliberadamente barato** — existe para
dizer qual é o próximo trabalho, e com que modelo e esforço rodá-lo, *enquanto
trocar ainda sai de graça*. Se gastar contexto analisando, destrói a própria
razão de ser.

1. `git pull`. **Conflito → pare e avise** antes de qualquer outra coisa.
   Mudança local não commitada não é motivo para parar: diga quais arquivos e
   siga (trabalho em andamento na mesma máquina é o caso normal).
2. **Reconheça a máquina** e anuncie na primeira linha da resposta. Rode
   `(Get-CimInstance Win32_VideoController).Name`:
   - GPU NVIDIA presente (RTX 4070 Super) → **Karen** (desktop, admin OK):
     máquina de runs — ambientes WSL2, tudo que precisa de GPU ou de R.
   - Só Intel Graphics → **Dell** (laptop, sem admin): análise e escrita.
     **Nunca** tentar WSL2 ou qualquer instalação que exija admin aqui.
   - Em dúvida (GPU inesperada), pergunte ao Igor em vez de assumir.
3. O ponteiro é o `docs/PROXIMO.md` e a fila inteira é o `docs/ROADMAP.md`
   (tabela até `<!-- HEADER-END -->`). **Se o hook `SessionStart` já injetou o
   bloco `docs/PROXIMO.md pede:`, use-o — não releia o arquivo.** Se o
   ponteiro apontar uma `maquina:` que não é esta, isso é a primeira coisa da
   resposta, e a alternativa é a primeira fatia `next` cuja `machine` seja
   `any`.
4. `git status --short` (idem: se veio na injeção, não rode de novo).
5. Responda em poucas linhas: o ID, o nome, o **modelo** e o **esforço**
   recomendados, e uma linha de objetivo. Pergunte se o Igor quer seguir assim.

**Não** leia `docs/STATUS.md`, `docs/PLAN.md` nem `BRIEF.md` na abertura. Eles
são lidos sob demanda, depois que a fatia foi escolhida — o `docs/ROADMAP.md`
traz o detalhe de cada C abaixo do marcador, e o `STATUS.md` traz o que falhou
e o que está preso a esta máquina.

## Ao encerrar a sessão

Executado pelo comando `/tchau`.

1. **`docs/ROADMAP.md`**: atualize a coluna `state` — o que fechou vira `done`,
   o próximo vira `next`, o que ficou pela metade vira `doing`. A tabela é a
   fila e nada mais; ela nunca explica.
2. **`docs/PROXIMO.md`**: avance o ponteiro **só se o `verificar:` da fatia
   aberta estiver satisfeito de verdade**. Se faltar qualquer item, não avance
   e diga o que faltou. `modelo:` e `esforco:` do ponteiro novo saem da tabela
   do roadmap, resolvidos na hora — nunca copiados do ponteiro anterior.
3. **`docs/STATUS.md`**: escreva o handoff narrativo — o que foi feito e em
   quais arquivos, o que ficou pela metade e onde exatamente parou, **o que foi
   tentado e falhou e por quê**, e o que está preso a esta máquina.
4. Confira `git status --porcelain`: nenhum segredo, nenhum arquivo acima de
   50 MB (outputs pesados de model run ficam em pasta ignorada).
5. Reaplique o teste do público a tudo que está entrando.
6. `git add -A`, commit descritivo em inglês, `git push`.
7. Termine dizendo a **próxima fase: ID, nome, modelo e esforço.** É a última
   coisa que o Igor lê na sessão.

O hook `guard_publication.py` recusa o commit se aparecer arquivo acima de
50 MB, caminho sob `outputs/`, ou a frase proibida. Bloqueio dele é sinal para
corrigir — nunca para contornar com `git add -f` ou mexendo no `.gitignore`.

## Infraestrutura Claude Code deste repo

Versionada em `.claude/` (o `.gitignore` deixa passar tudo menos o estado
local). Duas camadas: o **canon do playbook**, padronizado entre os projetos do
Igor (`/oi`, `/tchau`, `/360`, `hooks/sessao-abre.ps1`, os `deny` de segurança
e o par `docs/PROXIMO.md` + `docs/ROADMAP.md`), e o que é **só deste repo**,
abaixo. Ao mexer na infraestrutura: mudança que vale para todo projeto vai para
o playbook, não para cá.

- **`settings.json`** — união das duas camadas: os `deny` do canon, mais os
  três gates de Python liberados, `git push` sempre pergunta, `C:\chaves` /
  `~/chaves` negados, e `PYTHONUTF8=1`.
- **`hooks/guard_publication.py`** — bloqueia commit com arquivo grande,
  `outputs/`, ou a frase proibida na mensagem ou no diff.
- **`hooks/warn_py_syntax.py`** — avisa (não bloqueia) se um `.py` editado
  ficou com erro de sintaxe.
- **`/score`** — roda os três gates na ordem obrigatória: `simulation.checks`
  → `analysis/oracle.py` → `analysis/scoring.py`.
- **`publication-auditor`** — subagente adversarial. Rode antes de publicar
  qualquer coisa: ele tenta **reprovar** a peça, e devolve `SHIP` ou `BLOCK`.
