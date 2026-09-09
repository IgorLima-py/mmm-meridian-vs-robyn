# Próximo

Ponteiro de UMA fatia. A fila inteira está em `docs/ROADMAP.md` — este arquivo
é só o topo dela, resolvido agora. Lido pelo hook `SessionStart` e pelo `/oi`;
avançado pelo `/tchau` só depois que o `verificar:` abaixo estiver satisfeito.

chat: C3
titulo: Phase 5 — scoring e os três gráficos
perfil: julgamento analítico
modelo: opus
esforco: high
forma: sessao
maquina: any
plan-mode: nao
objetivo: Rodar o harness pré-registrado sobre todos os extratos commitados (Meridian, Robyn, os quatro degraus do oráculo) e construir os três gráficos que a Fase 5 do PLAN especifica — com o oráculo como terceira série, é isso que transforma empate em resultado.

## Contexto mínimo para abrir

- **C2 fechou nesta sessão** (gate C7 de sinal/ruído por canal em
  `simulation/checks.py`, WARN-only, piso 0.15 — ooh e display abaixo do piso
  em todos os 5 seeds, confirmando o achado do oráculo. Documentado em
  `docs/PLAN.md` §3 e `data/README.md`).
- C3 depende só do C1 (fechado: Robyn 102-104 a 4000×5, nenhum convergiu —
  `runs/robyn/DECISIONS.md`) — está desbloqueado.
- Ler `docs/PLAN.md` §6 (Fase 5) e `analysis/ORACLE.md` antes de escrever
  qualquer número: o oráculo já mostrou o enquadramento certo (tv/search/
  social são falha da ferramenta; ooh/display não são recuperáveis por
  ninguém) — os gráficos precisam refletir essa divisão, não escondê-la.
- Definition of done detalhada na entrada C3 do `docs/ROADMAP.md`.
