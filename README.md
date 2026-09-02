# Projeto Aplicado III — recomendação de treino

Universidade Presbiteriana Mackenzie  
Curso de Banco de Dados — 2026.2  
Disciplina: Projeto Aplicado III

Sistema de recomendação do próximo treino a partir do histórico de sessões de atividade física.

## Grupo

- Ana Clara Silva de Souza
- Cid Wallace Araujo de Oliveira
- Eduardo Machado Silva
- Frederico Ripamonte Borges (TIA 10740285)

## O que o sistema faz

Dado o histórico de treinos de uma pessoa (modalidade, duração, sequência), sugerir o próximo tipo de atividade. A base é o FitRec / Endomondo, publicada no repositório de sistemas de recomendação da UCSD (McAuley), citado no texto de apoio da disciplina.

- Usuários: `userId`
- Itens: modalidade (`sport`) e sessões de treino
- Interação implícita: o treino realizado
- Extras: timestamp, gênero, frequência cardíaca, GPS

Fonte: https://cseweb.ucsd.edu/~jmcauley/datasets/fitrec.html  
Paper: Ni, Muhlstein e McAuley, *Modeling heart rate and activity data for personalized fitness recommendation*, WWW 2019.

Caráter extensionista: ODS 3 — Saúde e bem-estar.

## Entregas

A Etapa 1 (capa, sumário parcial e introdução) usa o template oficial dos Avisos, arquivo `docs/templates/TEMPLATE_Modulo1.docx`. Prazo da professora: 4 de setembro de 2026.

## Estrutura

```
docs/templates/   templates oficiais das quatro etapas
data/raw/         base FitRec (não versionada)
data/processed/   recortes para treino
src/              código
```

## Licença de dados

O FitRec é para uso acadêmico. Não redistribuir nem usar comercialmente.
