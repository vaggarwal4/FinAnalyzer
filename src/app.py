
# coding: utf-8

# In[23]:

import sys
import time
from TwitterAPI import TwitterAPI
import json


consumer_key='7JPFei4tmTYgfIJLzT5Zpyk4V'
consumer_secret='8YFd8ubdCDujGdPf07LImNVdep9EShy1GiTkLVpgFoogl8KLuj'
access_token='2892695322-apzioNBM67pX7gOtubgzr1d6BNgZdTPaXRgOOIi'
access_token_secret='0DxllJkirFDclNkv8BeQssLEhd1UoHXR5F9UPtTXY0dZP'

tweet_list=[]
def get_twitter():
    return TwitterAPI(consumer_key, consumer_secret, access_token, access_token_secret)

def tweets(twitter, tweet_count):
    tweet = []
    while True:
        try:
            for response in twitter.request('statuses/filter',{'track':'new,bought,got,paid,purchase,transferred,exchange,loan,house,car,stocks,bonds,receive'}):
                if 'text' in response:
                        tweet.append(response)
                        if len(tweet) % 100 == 0:
                            print('found %d tweet' % len(tweet))
                        if len(tweet) >= tweet_count:
                            return tweet
        except:
            print("Unexpected error:", sys.exc_info()[0])
    return tweet


def robust_request(twitter, resource, params, max_tries=5):
    for x in range(max_tries):
        request = twitter.request(resource, params)
        if request.status_code == 200:
            return request
        else:
            with open('sparta_result', 'w') as fout:
                json.dump(tweet_list, fout)

            print('Got error %s \nsleeping for 15 minutes.' % request.text)
            sys.stderr.flush()
            time.sleep(60 * 15)
            
    


# In[24]:

twitter = get_twitter()
print('Connection established')
tweet = tweets(twitter,500000)


# In[25]:

collect=[]
lists=[]
user=[]
l=['bought','got','new','paid','purchased','return','transferred','receive']
for i in range(len(l)):
    lists.append([])
    user.append([])
for i in range(len(l)):
    for j in range(len(tweet)):
         if l[i] in tweet[j]['text']:
                collect.append(l[i])
                lists[i].append(tweet[j]['text'])
                user[i].append(tweet[j]['user']['name'])
with open('tweet_data','w') as outfile:
    json.dump(lists,outfile)
with open('collect_data','w')as outfile:
    json.dump(collect,outfile)
with open('user_data','w') as outfile:
    json.dump(user,outfile)


# In[27]:

from collections import Counter
for n,i in enumerate(collect):
    if i=='bought' or i == 'new'or i=='paid' or i=='purchased':
        collect[n]='bought'
    if i=='got' or i=='receive':
        collect[n]='receive'
bucket=Counter(collect)
import json 
with open('bucket', 'w') as outfile:
    json.dump(bucket, outfile)


# In[15]:

#chec=[1,2,3,4,4,5,6,7,8,2,1]
import json
with open('tweet_data') as data_file:    
    tweet = json.load(data_file)
tweet[0]   


# In[30]:

tu=user[0]+user[1]+user[2]+user[3]+user[4]+user[5]+user[6]
active=Counter(tu)
from itertools import dropwhile
for key, count in dropwhile(lambda key_count: key_count[1] >= 2, active.most_common()):
    del active[key]
    
print(len(active),int(len(tu)-len(active)))    
dict_seg={'pro-active':len(active),'rest':int(len(tu)-len(active))}
with open('segmentation', 'w') as outfile:
    json.dump(dict_seg, outfile)


# In[31]:

import re
from pprint import pprint
def tokenize(s):
    return re.sub('\W+', ' ', s).lower().split() if s else []
bought=lists[0]+lists[1]+lists[2]+lists[3]
bought_words=Counter()
for p in bought:
    bought_words.update(Counter(tokenize(p)))


# In[32]:

check=['house','car','card','job','stocks','loan','bike','insurance','lottery','bonds']
new_dict = {k: bought_words[k] for k in check if k in bought_words}
with open('potential_customer', 'w') as outfile:
    json.dump(new_dict, outfile)


# In[33]:

#sentiment analysis
import sys
import time
from TwitterAPI import TwitterAPI
import json
import re
import pandas as pd
from collections import defaultdict
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen

def afinn_download():
    url = urlopen('http://www2.compute.dtu.dk/~faan/data/AFINN.zip')
    zipfile = ZipFile(BytesIO(url.read()))
    afinn_file = zipfile.open('AFINN/AFINN-111.txt')

    afinn = dict()

    for line in afinn_file:
        parts = line.strip().split()
        if len(parts) == 2:
            afinn[parts[0].decode("utf-8")] = int(parts[1])
    return afinn

def afinn_sentiment2(terms, afinn, verbose=False):
    pos = 0
    neg = 0
    for t in terms:
        if t in afinn:
            if verbose:
                print('\t%s=%d' % (t, afinn[t]))
            if afinn[t] > 0:
                pos += afinn[t]
            else:
                neg += -1 * afinn[t]
    return pos, neg

def sentiment_analysis(tweet,afinn):
    tweet_pos=[]
    tweet_neg=[]
    for i in range(len(tweet)):
        terms=tweet[i]['text'].split()
        pos,neg=afinn_sentiment2(terms, afinn, verbose=False)
        if pos>neg:
            tweet_pos.append(tweet[i])
        else:
            tweet_neg.append(tweet[i])
    return tweet_pos,tweet_neg


# In[41]:

afinn=afinn_download()
p,n=sentiment_analysis(tweet,afinn)


# In[55]:

pos=[]
neg=[]
for i in range(len(p)):
    d={'text':p[i]['text'],'user':p[i]['user']['name']}
    pos.append(d)
for i in range(int(len(n)/3)):
    d={'text':n[i]['text'],'user':n[i]['user']['name']}
    neg.append(d)
    
    


# In[52]:

with open('posTweet','w') as outfile:
    json.dump(pos,outfile)
with open('negTweet','w') as outfile:
    json.dump(neg,outfile)    


# In[57]:

len(pos)


# In[261]:

from collections import defaultdict
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen

url = urlopen('http://www2.compute.dtu.dk/~faan/data/AFINN.zip')
zipfile = ZipFile(BytesIO(url.read()))
afinn_file = zipfile.open('AFINN/AFINN-111.txt')

afinn = dict()

for line in afinn_file:
    parts = line.strip().split()
    if len(parts) == 2:
        afinn[parts[0].decode("utf-8")] = int(parts[1])

print('read %d AFINN terms.\nE.g.: %s' % (len(afinn), str(list(afinn.items())[:10])))

