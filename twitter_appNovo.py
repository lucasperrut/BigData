import socket
import sys
import requests
import requests_oauthlib
import json

# Replace the values below with yours
BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAGtzWgEAAAAAyYiQwfL65CvUsatg5W3vlq%2BeqFw%3DLwIbRxb5g2UbYwjRY29UujuKVLj3KMaTiB2hq4Z8p8uAXO3N4v'
ACCESS_TOKEN = '323583152-XJdrCrzA0v1hr1Tz6Cca8ZsZRJlGtRkkJ9MbUMH5'
ACCESS_SECRET = 'qITlw0WThKXORRrwQr1lZuny2oBBMwAfH5Mm1hBuVvLhg'
CONSUMER_KEY = 'z70iGevYFS5PPWm1Co6W1w2ZN'
CONSUMER_SECRET = 'mTYTF3YNfwjNrMQ3WWb8T481SL1Hzf8L64xGO4Ubs0HtlrxosF'

my_auth = requests_oauthlib.OAuth1(CONSUMER_KEY, CONSUMER_SECRET,ACCESS_TOKEN, ACCESS_SECRET)


def send_tweets_to_spark(http_resp, tcp_connection):
    for line in http_resp.iter_lines():
        try:
            full_tweet = json.loads(line)
            tweet_text = full_tweet['text'] + '\n'
            print("Tweet Text: " + tweet_text)
            print ("------------------------------------------")
            tcp_connection.send(tweet_text)
        except:
            e = sys.exc_info()[0]
            print("Error: %s" % e)


def get_tweets():
    url = 'https://stream.twitter.com/1.1/statuses/filter.json'
    #query_data = [('language', 'en'), ('locations', '-130,-20,100,50'),('track','#')]
    query_data = [('locations', '-122.75,36.8,-121.75,37.8,-74,40,-73,41'), ('track', '#')] #this location value is San Francisco & NYC
    query_url = url + '?' + '&'.join([str(t[0]) + '=' + str(t[1]) for t in query_data])
    response = requests.get(query_url, auth=my_auth, stream=True)
    print(query_url, response)
    return response


TCP_IP = "localhost"
TCP_PORT = 9009
conn = None
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
print("Waiting for TCP connection...")
conn, addr = s.accept()
print("Connected... Starting getting tweets.")
resp = get_tweets()
send_tweets_to_spark(resp,conn)

#resp = get_tweets()
#for line in resp.iter_lines():
#      try:
#          full_tweet = json.loads(line)
#          #print(full_tweet)
#          tweet_text = full_tweet['text'] + '\n' # pyspark can't accept stream, add '\n'
#          print("Tweet Text: " + tweet_text)
#          #print ("------------------------------------------")
#      except:
#          e = sys.exc_info()[0]
#          print("Error: %s" % e)
