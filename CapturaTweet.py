import socket
import sys
import json
from datetime import date
from types import SimpleNamespace
import requests
import requests_oauthlib

def Config():
    with open('config.json', 'r') as f:
        config = json.load(f)
        return config

config = Config()

def EnviarParaSpark(msg, tcp_connection):
    try:
        print("Msg: " + msg)
        tcp_connection.send(msg.encode('utf-8'))
    except:
        e = sys.exc_info()[0]
        print("Erro ao enviar: %s" % e)

def ProcessarMsg(response, tcp_connection):
    palavrasChave = config['Palavras_Chave'].split(",")
    linhas = response.iter_lines()
    for l in linhas:
        try:
            registro = json.loads(l)
            tweet = registro['text']
            if(config['Filtrar']):
                for t in palavrasChave:
                    if(t in tweet):
                        EnviarParaSpark(tweet, tcp_connection)
            else:
                   EnviarParaSpark(tweet, tcp_connection)
        except:
            e = sys.exc_info()[0]
            print("Erro ao processar: %s" % e)

def BuscarTweets():

    url = 'https://stream.twitter.com/1.1/statuses/filter.json'
    query_data = [
        ('language', config['Idioma']),
        ('locations', config['Local_Busca']),
        ('track', config['Palavras_Chave'])
    ]
    query_url = url + '?' + '&'.join([str(t[0]) + '=' + str(t[1]) for t in query_data])
    response = requests.get(query_url, auth=user_auth, stream=True)
    print(query_url, response)
    return response

if __name__ == '__main__':
    
    conta = config['ContaTwitter']
    user_auth = requests_oauthlib.OAuth1(conta['Consumer_Key'], conta['Consumer_Secret'], conta['Acess_Token'], conta['Acess_Secret'])
    
    streamConf = config['SparkStream']
    hostStr = str(streamConf['IP']) + ":" + str(streamConf['Porta'])
    conn = None
    _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _socket.bind((streamConf['IP'], streamConf['Porta']))
    _socket.listen(1)
    print("Aguardando conexão do socket em: %s" % hostStr)
    conn, addr = _socket.accept()
    print("Conectado no IP: %s." % hostStr)
    print("Iniciando buscas no Twitter [%s]" % date.today())
    resp = BuscarTweets()
    print("Busca concluida [%s] " % date.today())
    ProcessarMsg(resp, conn)
