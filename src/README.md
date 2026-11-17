# Código

`fitrec_poc.py` lê o recorte filtrado do FitRec em fluxo, monta a matriz usuário–modalidade e calcula quatro listas: vizinhança de itens, hábito do próprio usuário, popularidade e a soma do hábito com a vizinhança.

O arquivo de cerca de 4,9 GB não entra no repositório. O script baixa o endereço público, descarta GPS, frequência cardíaca e velocidade, e não grava o JSON.

A saída vai para `resultados/prova-de-conceito.json` e `resultados/reavaliacao.json`.

Na raiz do repositório:

```bash
python3 -m pip install -r requirements.txt
python3 src/fitrec_poc.py
```

Biblioteca usada no experimento: Python 3 e numpy.
