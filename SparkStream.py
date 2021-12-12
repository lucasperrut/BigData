import sys
from datetime import datetime
import requests
import json
from marshmallow import Schema, fields

from pyspark import SparkConf, SparkContext
from pyspark.streaming import StreamingContext
from pyspark.sql import Row, SQLContext



def Config():
    with open('config.json', 'r') as f:
        config = json.load(f)
        return config

sparkConf = Config()['Spark']

if(sparkConf['Local']):
    localStr = 'local[' + str(sparkConf['Instacia_Local']) + ']'
    spc = SparkContext(localStr, sparkConf['AppName'])
else:
    spc = SparkContext(master=(sparkConf['Master_IP']+':'+sparkConf['Master_Porta']),appName=sparkConf['AppName'])
spc.setLogLevel("ERROR")

spsc = StreamingContext(spc, 2)

spsc.checkpoint("CheckPoint_SparkTwitter")

streamConf = Config()['SparkStream']
dataStream = spsc.socketTextStream(streamConf['IP'], streamConf['Porta'])


def aggr_tags_count(new_values, total_sum):
    return sum(new_values) + (total_sum or 0)

def get_sqlcontext_instance(spark_context):
    if 'sqlContextSingletonInstance' not in globals():
        globals()['sqlContextSingletonInstance'] = SQLContext(spark_context)
    return globals()['sqlContextSingletonInstance']

def getUrl():
    webServerConf = Config()['WebServer']
    url = ''
    if(webServerConf['SSL']):
        url+= 'https://'
    else:
        url+= 'http://'
    url+= (webServerConf['IP'] + ':' + str(webServerConf['Porta']) + '/')
    #print(url)
    return url
url = getUrl()

class Mencao:
    def __init__(self, t, c):
        self.text = t
        self.count = c
class ObjectSchema(Schema):
    text = fields.Str()
    count = fields.Str()


def enviarParaPainel(df, df2):
    #print(df.select("hashtag").collect())
    #print(df.select("count").collect())
    # print(df)
    print(df2)
    if((df is not None) and (df2 is not None)):
        tags = [str(h[0]) for h in df.select("mencao").collect()]
        tagsCount = [c[0] for c in df.select("count").collect()]
        df2Rows = df2.collect()
        listMencoes = [(Mencao(row[0], str(row[1]))) for row in df2Rows]
        #print(listMencoes)
        objMencao = ObjectSchema()
        palavrasMerge = objMencao.dumps(listMencoes, many=True)
        #print(palavrasMerge)
        request_data = {'label': str(tags), 'data': str(tagsCount), 'palavrasTup' : str(palavrasMerge) }
        #print(request_data)
        response = requests.post(url + 'atualizarPainel', data=request_data)
        print('Enviando para PAINEL request_data: %s ' % request_data)

hashtagsDf = None
mencaoDf = None


def ProcessarRDD(time, rdd2):
    try:
        sql_context2 = get_sqlcontext_instance(rdd2.context)
        row_rdd = rdd2.map(lambda w: Row(mencao=w[0], count=w[1], timestamp=datetime.now().strftime('%Y/%m/%d %H:%M:%S')))
        if (row_rdd.isEmpty() == False):
            mencoes_df = sql_context2.createDataFrame(row_rdd)
            mencoes_df.registerTempTable("mencoes")
            mencoes_counts_dataf = sql_context2.sql("select mencao as mencao, count as count from mencoes order by count desc limit 500")
            mencoes_counts_dataf.show()
            hashtag_counts_dataf = sql_context2.sql("select mencao, count, timestamp  from mencoes where mencao like '#%' order by count desc limit 10")
            hashtag_counts_dataf.show()
            hashtagsDf = hashtag_counts_dataf
            mencaoDf = mencoes_counts_dataf
            enviarParaPainel(hashtagsDf, mencaoDf)

    except:
        e = sys.exc_info()
        print("Erro processando rdd2: %s" % e[0])
        print(e)
sys.setrecursionlimit(1500)
print(sys.getrecursionlimit())
words = dataStream.flatMap(lambda line: line.split(" "))
words.pprint()

wordsMap = words.map(lambda x: (x, 1))
wordsReduce = wordsMap.filter(lambda x: ' ' not in x).reduceByKey(lambda x,y: x+y )
words_total = wordsReduce.updateStateByKey(aggr_tags_count)

words_total.foreachRDD(ProcessarRDD)
spsc.start()
spsc.awaitTermination()