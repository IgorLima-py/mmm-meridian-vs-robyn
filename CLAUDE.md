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

Executado pelo comando `/oi`.

1. **Reconheça a máquina** e anuncie na primeira linha da resposta. Rode
   `(Get-CimInstance Win32_VideoController).Name`:
   - GPU NVIDIA presente (RTX 4070 Super) → **Karen** (desktop, admin OK):
     máquina de runs — Fases 1, 3 e 4 do PLAN, ambientes WSL2.
   - Só Intel Graphics → **Dell** (laptop, sem admin): Fases 2, 5 e 6.
     **Nunca** tentar WSL2 ou qualquer instalação que exija admin aqui.
   - Em dúvida (GPU inesperada), pergunte ao Igor em vez de assumir.
2. `git pull` e `git log --oneline -5`.
3. Leia `docs/STATUS.md` por inteiro; na primeira vez, leia também `BRIEF.md`.
4. `git status --short`.
5. Diga onde paramos e qual é o próximo passo concreto **para esta máquina**
   (o STATUS e o PLAN dizem qual fase pertence a qual máquina).

## Ao encerrar a sessão

Executado pelo comando `/tchau`.

1. Escreva o handoff em `docs/STATUS.md`: o que foi feito, o que ficou pela metade,
   o que falhou e por quê, o próximo passo concreto.
2. Confira `git status --porcelain`: nenhum segredo, nenhum arquivo acima de 50 MB
   (outputs de model run grandes ficam em pasta ignorada).
3. Reaplique o teste do público a tudo que está entrando.
4. `git add -A`, commit descritivo em inglês, `git push`.
