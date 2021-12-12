# Trabalho de Big Data
API do Twiter em Tempo Real para fazer Análises.
Trabalho desenvolvido para o MBA em Engenharia de Software/UFRJ.

## Tweets
Foi usado o __Tweepy__ para a integração com a api do tweeter obtendo os dados em tempo real para execução de analise do spark:

## Executando
- Edite o arquivo `config.json`

- Execute os seguintes `.py`:
  - CapturaTweet.py
  - SparkStream.py
  - PainelHost.py

- Abra o a URL `http://localhost:5001/`

```
    python3 CapturaTweet.py

    python3 SparkStream.py

    python3 PainelHost.py
```
