# O próximo treino

Sistema de recomendação da próxima modalidade de atividade física, a partir do histórico de sessões.

Universidade Presbiteriana Mackenzie  
Faculdade de Computação e Informática  
Curso de Banco de Dados — 2026.2  
Disciplina: Projeto Aplicado III  
Professor orientador: Gustavo Scalabrini Sampaio

## Entrega final

| | Link |
|---|---|
| Vídeo de apresentação | https://youtu.be/LI8NvARRv4s |
| Vídeo da aplicação na comunidade | https://youtu.be/TyZ9lBCS5rE |
| Demonstração online | https://fredericorbgs.github.io/projeto-aplicado-iii-treino/app/ |
| Documento da etapa 4 | [`docs/etapa-4/a4-aplicando-conhecimento.docx`](docs/etapa-4/a4-aplicando-conhecimento.docx) |
| Slides da apresentação | [`docs/etapa-4/a4-slides-apresentacao.pdf`](docs/etapa-4/a4-slides-apresentacao.pdf) |

## Objetivo

Ranquear a próxima modalidade de uma pessoa e medir se uma vizinhança de itens supera a lista global e a repetição da modalidade que essa pessoa mais fez.

A base é o recorte filtrado do FitRec (Endomondo), de Ni, Muhlstein e McAuley (WWW 2019). O uso é acadêmico. O arquivo de cerca de 4,9 GB não está neste repositório e não pode ser redistribuído.

Página da base: https://cseweb.ucsd.edu/~jmcauley/datasets/fitrec.html

## Grupo

| Integrante | TIA | E-mail |
|---|---|---|
| Ana Clara Silva de Souza | 10748729 | 10748729@mackenzista.com.br |
| Cid Wallace Araujo de Oliveira | 10748009 | 10748009@mackenzista.com.br |
| Eduardo Machado Silva | 10748011 | 10748011@mackenzista.com.br |
| Frederico Ripamonte Borges | 10740285 | 10740285@mackenzista.com.br |

## Pastas

| Pasta | O que tem |
|---|---|
| `docs/etapa-1/` | Documento da etapa 1 e o desenho do pipeline |
| `docs/etapa-2/` | Documento da etapa 2 |
| `docs/etapa-3/` | Documento da etapa 3 |
| `docs/etapa-4/` | Documento da etapa 4, com resultados e conclusão, e os slides da apresentação |
| `docs/etapa-4/videos/` | Cópias dos dois vídeos publicados no YouTube |
| `docs/templates/` | Templates oficiais usados na formatação |
| `src/` | Código que gera as métricas e o modelo da demonstração |
| `app/` | Demonstração local: abra `app/index.html` no navegador |
| `resultados/` | Números e figuras citados no documento da etapa 4 |
| `data/raw/` e `data/processed/` | Vazias de propósito. A base bruta não é versionada |

O documento para leitura da etapa final é `docs/etapa-4/a4-aplicando-conhecimento.docx`.

## Como reproduzir

```bash
python3 -m pip install -r requirements.txt
python3 src/fitrec_poc.py
```

A leitura do arquivo remoto leva vários minutos. As métricas já calculadas estão em `resultados/`.

## Demonstração

Online: https://fredericorbgs.github.io/projeto-aplicado-iii-treino/app/

Sem internet, abra `app/index.html` no navegador. A pessoa toca nas modalidades das últimas sessões e vê as quatro listas do documento mudarem a cada toque. Detalhes em `app/README.md`.

## Vídeos

| Vídeo | YouTube | Cópia no repositório |
|---|---|---|
| Apresentação, com os quatro integrantes | https://youtu.be/LI8NvARRv4s | `docs/etapa-4/videos/apresentacao.mp4` |
| Aplicação na comunidade | https://youtu.be/TyZ9lBCS5rE | `docs/etapa-4/videos/aplicacao-comunidade.mp4` |

No vídeo da aplicação, um integrante do grupo que corre e pedala insere na página uma rotina simulada de quatro semanas e lê as quatro listas. Depois testa a sessão seguinte e uma troca hipotética para musculação.
