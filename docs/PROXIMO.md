# Próximo

Ponteiro de UMA fatia. A fila inteira está em `docs/ROADMAP.md` — este arquivo
é só o topo dela, resolvido agora. Lido pelo hook `SessionStart` e pelo `/oi`;
avançado pelo `/tchau` só depois que o `verificar:` abaixo estiver satisfeito.

chat: C2
titulo: Recoverability gate — the check that would have caught this
perfil: execução mecânica
modelo: sonnet
esforco: medium
forma: sessao
maquina: any
plan-mode: nao
objetivo: Adicionar um piso de sinal/ruído por canal ao `simulation/checks.py` e registrar o oráculo como passo pré-run, para que nenhum cenário futuro chegue a uma GPU antes de alguém saber se a verdade dele é recuperável.
verificar: `python -m simulation.checks` sai 0 e imprime uma linha de sinal/ruído por canal para cada seed, e `grep -c 'signal-to-noise' docs/PLAN.md data/README.md` retorna diferente de zero para os dois arquivos.

## Contexto mínimo para abrir

- `python -m simulation.checks` já roda hoje um gate de variância total de mídia
  ([0.10, 0.35]); falta o gate **por canal**. Os cinco seeds passam no gate
  atual com ~85% do sinal de mídia concentrado num canal só e quatro canais
  abaixo de 1% cada — o oráculo (`analysis/ORACLE.md`) já mostrou que dois
  desses quatro (ooh, display) não são recuperáveis por nenhum estimador.
- **Warn, não fail:** o cenário v1 tem dois canais abaixo do piso e isso é um
  achado documentado, não uma regressão — o gate deve avisar, nunca travar
  o pipeline por causa disso.
- Documentar o gate em `docs/PLAN.md` §3 e `data/README.md`, e referenciar
  `analysis/ORACLE.md` a partir do `docs/PLAN.md` como passo pré-registrado
  para qualquer cenário futuro.
- **C1 fechou nesta sessão** (Robyn 102-104 escalados a 4000×5, nenhum
  convergiu — achado documentado em `runs/robyn/DECISIONS.md`). C3 também
  está liberado agora (`next`, opus/high) — mas é trabalho de julgamento
  analítico, perfil diferente deste ponteiro; só abrir C3 se o Igor pedir
  explicitamente em vez de C2.
