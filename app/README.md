# Demonstração local

Página para mostrar o recomendador a quem treina. Online em https://fredericorbgs.github.io/projeto-aplicado-iii-treino/app/. Sem internet, abra `index.html` no navegador, com duplo clique.

A pessoa toca nas modalidades das últimas sessões e vê, a cada toque, as quatro listas avaliadas no documento: hábito, vizinhança de itens, soma do hábito com a vizinhança e popularidade. O campo "Qual foi o treino seguinte?" mostra em que posição de cada lista estava a sessão que ela fez de fato.

As contas são as de `src/fitrec_poc.py`: contagem da pessoa, cosseno entre modalidades com a diagonal em 1, popularidade do treino e soma com cada lista dividida pelo próprio máximo. A posição usa a mesma regra de empate: 1 mais o número de modalidades com nota estritamente maior.

`modelo.js` guarda só agregados do treino: os nomes das modalidades, a popularidade e a matriz de cosseno. Não há linha de usuário. Para gerar de novo, na raiz do repositório:

```bash
python3 src/exportar_modelo.py
```

O script lê o FitRec filtrado em fluxo e, antes de gravar, confere as métricas com `resultados/reavaliacao.json`.

Os nomes em português são só de exibição. O rótulo do arquivo aparece ao lado, em letra menor.
