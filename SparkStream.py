import sys
from datetime import datetime
import requests
import json

from pyspark import SparkConf, SparkContext
from pyspark.streaming import StreamingContext
from pyspark.sql import Row, SQLContext



def Config():
    with open('config.json', 'r') as f:
        config = json.load(f)
        return config

sparkConf = Config()['Spark']

if(sparkConf['Local']):
    spc = SparkContext("local[2]", "PAINELTWITTER")
else:
    spc = SparkContext(master=(sparkConf['Master_IP']+':'+sparkConf['Master_Porta']),appName="PAINELTWITTER")
spc.setLogLevel("ERROR")

spsc = StreamingContext(spc, 2)

spsc.checkpoint("CheckPoint_SparkTwitter")

streamConf = Config()['SparkStream']
dataStream = spsc.socketTextStream(streamConf['IP'], streamConf['Porta'])


def aggr_tags_count(new_values, total_sum):
    '''
    The function 'aggr_tags_count' aggregates and sum up the hashtag counts
    collected for each category
    '''
    return sum(new_values) + (total_sum or 0)

def get_sqlcontext_instance(spark_context):
    '''
    Create sql context object globally (singleton object)
    '''
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
    print(url)
    return url
url = getUrl()

def send_df_to_dashboard(df):
    # extract the hashtags from dataframe and convert them into array
    print(df.select("hashtag").collect())
    print(df.select("count").collect())
    top_tags = [str(h[0]) for h in df.select("hashtag").collect()]
    # extract the counts from dataframe and convert them into array
    #tags_count = [p.count for p in df.select("count").collect()]
    tags_count = [c[0] for c in df.select("count").collect()]
    # initialize and send the data through REST API
    request_data = {'label': str(top_tags), 'data': str(tags_count)}
    print(request_data)
    response = requests.post(url + 'updateData', data=request_data)

def rdd_process(time, rdd):
    print("~~~~~~~~~~~~~~ %s ~~~~~~~~~~~~~~" % str(time))
    try:
        # Get spark sql singleton context from the current context
        print(rdd)
        sql_context = get_sqlcontext_instance(rdd.context)
        # convert the RDD to Row RDD
        row_rdd = rdd.map(lambda w: Row(hashtag=w[0], count=w[1], timestamp=datetime.now().strftime('%Y/%m/%d %H:%M:%S')))
        if row_rdd.isEmpty():
            print('RDD is empty')
        else:
            # create a DF from the Row RDD
            hashtags_df = sql_context.createDataFrame(row_rdd)
            # Register the dataframe as table
            hashtags_df.registerTempTable("hashtags")
            # get the top 10 hashtags from the table using SQL and print them
            hashtag_counts_dataf = sql_context.sql("select hashtag, count, timestamp  from hashtags order by count desc limit 10")
            hashtag_counts_dataf.show()
            # call this method to send them to elasticsearch
            #send_dataframe_to_elasticsearch(hashtags_df)
            send_df_to_dashboard(hashtag_counts_dataf)
            #print("teste")
    except:
        e = sys.exc_info()
        print("Error: %s" % e[0])
        print("Erro2: %s" % e[1])
        print(e)
        

# split each tweet into individual words to create category
words = dataStream.flatMap(lambda line: line.split(" "))
words.pprint()
# filter the words to get only hashtags from tweets, then to map each hashtag to be paired of with (hashtag,1)
hashtags = words.filter(lambda w: '#' in w).map(lambda x: (x, 1))
print("hashtags: ")
hashtags.pprint()
# Sum up each of the count of hashtag to its last count
tags_totals = hashtags.updateStateByKey(aggr_tags_count)
print("tags_totals")
tags_totals.pprint()
# Perform processing for each RDD generated in each interval
tags_totals.foreachRDD(rdd_process)

# start the streaming computation
spsc.start()
# wait for the streaming to finish
spsc.awaitTermination()
