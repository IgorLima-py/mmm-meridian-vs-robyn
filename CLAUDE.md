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

## A primeira sessão — planejamento (antes de qualquer código)

Esta pasta ainda não tem plano. A primeira sessão de trabalho:

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

1. `git pull` e `git log --oneline -5`.
2. Leia `docs/STATUS.md` por inteiro; na primeira vez, leia também `BRIEF.md`.
3. `git status --short`.
4. Diga onde paramos e qual é o próximo passo concreto.

## Ao encerrar a sessão

Executado pelo comando `/tchau`.

1. Escreva o handoff em `docs/STATUS.md`: o que foi feito, o que ficou pela metade,
   o que falhou e por quê, o próximo passo concreto.
2. Confira `git status --porcelain`: nenhum segredo, nenhum arquivo acima de 50 MB
   (outputs de model run grandes ficam em pasta ignorada).
3. Reaplique o teste do público a tudo que está entrando.
4. `git add -A`, commit descritivo em inglês, `git push`.
