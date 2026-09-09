# Próximo

Ponteiro de UMA fatia. A fila inteira está em `docs/ROADMAP.md` — este arquivo
é só o topo dela, resolvido agora. Lido pelo hook `SessionStart` e pelo `/oi`;
avançado pelo `/tchau` só depois que o `verificar:` abaixo estiver satisfeito.

chat: C1
titulo: Robyn escalation — all five seeds on one documented spec
perfil: execução mecânica
modelo: sonnet
esforco: medium
forma: sessao
maquina: karen
plan-mode: nao
objetivo: Rodar a escalada 4000x5 pendente para os seeds 102, 103 e 104, para que os cinco extratos do Robyn parem de ser um misto de dois specs.
verificar: `python analysis/scoring.py --results runs --data data/sim --out analysis/out` sai 0, os três JSONs `runs/robyn/results/robyn_national_seed10{2,3,4}.json` registram 4000 iterações cada, e a emenda RD em `runs/robyn/DECISIONS.md` tem linha de fechamento datada nomeando o resultado de convergência de cada seed.

## Contexto mínimo para abrir

Comando, nesta máquina (Karen), ~20 min por seed, desatendido:

```
wsl -d Ubuntu -u igor --cd /mnt/c/<repo> -- Rscript runs/robyn/run_robyn.R --iterations=4000 102 103 104
```

Nunca passar `quiet` — crasha no Robyn 3.12.1 (fricção F8, `envs/ENVIRONMENT.md`).

**Se esta não for a Karen:** C2 é a fatia paralela e roda em qualquer máquina
(piso de sinal/ruído por canal no `simulation/checks.py`). Não abra C3 em
diante — todas dependem do C1 fechar.

**Se a escalada não puder rodar:** o fallback pré-registrado é reverter o
seed101 para o run 2000x5, para que os cinco compartilhem o spec original.
Publicar o misto sem explicar, não.
