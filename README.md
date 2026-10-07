# Mind Map Interativo — Caso DataPulse Soluções

Mind map interativo em Python/Streamlit para apresentação da **Fase 1** do trabalho
sobre ética e tecnologia (Grupo 1 — Comitê Técnico de Crise e Conduta).

## Sobre o caso

Situação-Problema 1: **O Algoritmo de Avaliação de Desempenho**, envolvendo:
- Monitoramento invasivo de colaboradores em home office (captura de tela e ritmo de digitação)
- Viés algorítmico em ferramenta de triagem de currículos do RH (descarte por bairro e idade)

## Estrutura do mind map

- Situações-problema (Home office / RH)
- Análise técnica
- Análise ética
- Análise comportamental
- Análise legal (LGPD, CF, CLT)
- Glossário de conceitos
- Matriz de mapeamento
- Consolidação do diagnóstico

## Tecnologias

- [Python](https://www.python.org/)
- [Streamlit](https://streamlit.io/)
- [streamlit-agraph](https://github.com/ChrisDelClea/streamlit-agraph)

## Como rodar localmente

1. Clone o repositório:
```bash
   git clone <https://github.com/giiov/map-eco>
   cd <map-eco>
```
2. Crie e ative um ambiente virtual (opcional, mas recomendado):
```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Mac/Linux
```
3. Instale as dependências:
```bash
   pip install -r requirements.txt
```
4. Rode a aplicação:
```bash
   streamlit run app.py
```

## Deploy

Publicado via [Streamlit Community Cloud](https://streamlit.io/cloud).
Link: [mind-map](https://mind-map-eco.streamlit.app/)

## Grupo

Grupo 1 — Comitê Técnico de Crise e Conduta - 3°AMS
- Antonella Prucoli
- Bruno Holanda
- Emilly Vitória
- Giovana Hermelinda Cipulo
- Heloisa Fernandes
- Heloisa Torres
- Maria Eduarda Chella
- Matheus Amorim