# Próximo

> Este arquivo é **lido por regex**, não por humano. Uma chave por linha, `chave: valor`, sem
> markdown, sem lista, sem negrito. O que vier depois de `#` é comentário e é ignorado.
>
> Quem lê: o hook de abertura do plugin `playbook` (`sessao-abre.ps1`), e o `/oi` quando não há hook.
> Quem escreve: o `/tchau`, ao avançar o ponteiro, e o `/360`, ao desenhar o roadmap.
> A fatia inteira (entra, sai, verificar, prompt de abertura) está no bloco 3 do `docs/ROADMAP.md`.

chat: C12
titulo: Alocadores das ferramentas nos modelos da v1, contra o ótimo verdadeiro
perfil: padrao
modelo: sonnet
esforco: medium
forma: sessao
maquina: Karen
plan-mode: nao
persona: engenheiro de ML que conhece o Robyn e o Meridian por dentro
objetivo: Rodar robyn_allocator() e o BudgetOptimizer do Meridian 1.8.0 sobre os modelos da v1 já salvos em outputs/, sem refit, com regret.BOUNDS["primary"], e gravar 10 JSONs de alocação no formato do RESULTS_SCHEMA.md (seção Allocation files); o regret.py já os pontua.
