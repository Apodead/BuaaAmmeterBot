from html.parser import HTMLParser
from html.entities import name2codepoint
import requests
import json
from pyquery import PyQuery as pq

url = "http://shsd.buaa.edu.cn/PubBuaa"

def query_usage(mid):
    req = requests.get(url,params={'id':mid})
    if req.status_code == requests.codes.ok :
        html = pq(req.text)
    #html = pq(url,{'id':mid})
    
    ## Recent usage
    remain, yesterday_usage = \
            html('tspan').text().split()
    s13_split = html('script').eq(13).text().split()
    
    ## History usage data
    index_date = s13_split.index('data:')+1                #index_date = 40
    index_usage = s13_split.index('data:',index_date)+1    #index_usage = 52
    history_date = json.loads(s13_split[index_date])
    history_usage = json.loads(s13_split[index_usage])
    history = dict((history_date[i],history_usage[i]) \
            for i in range(len(history_date)))
    
    ## Top-up data
    topup = html('tbody').text().replace('\n',' ')
    
    return remain, \
            yesterday_usage, \
            history, \
            topup

def getIdData():
    #iddata_url = "http://shsd.buaa.edu.cn/PubBuaa/QueryIdData"
    IdData_json = requests.get(url+'/QueryIdData')
    IdData = json.loads(IdData_json.text)
    return IdData

