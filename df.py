from html.parser import HTMLParser
from html.entities import name2codepoint
import requests
import json
import sqlite3
import datetime

class myParser(HTMLParser):
    tspan = False
    tspan_count = 0
    script = False
    script_count = 0
    def handle_starttag(self,tag,attrs):
        if tag == "tspan":
            self.tspan = True
            self.tspan_count += 1
        if tag == "script":
            self.script = True
            self.script_count += 1
        if tag == "html":
            self.tspan_count = 0
    def handle_endtag(self,tag):
        if tag == "tspan":
            self.tspan = False
        if tag == "script":
            self.script = False
    def handle_data(self,data):
        if self.tspan:
            if self.tspan_count == 1:
                print("剩余电量：" + data + "kWh")
                self.remain=data
            if self.tspan_count == 2:
                print("昨日用电：" + data + "kWh")
                self.yesterday_usage=data
        if self.script and self.script_count == 14:
            #print(data)
            data=data.split()
            self.history_date=json.loads(data[40])
            self.history_usage=json.loads(data[52])
        return
    
def queryByID(id):
    p = myParser()
    url = "http://shsd.buaa.edu.cn/PubBuaa"
    payload = { 'id':id }
    req = requests.get(url, params=payload)
    print("电表ID: " + str(id))
    p.feed(str(req.content))

def getIdData():
    url = "http://shsd.buaa.edu.cn/PubBuaa/QueryIdData"
    IdData_json = requests.get(url)
    IdData = json.loads(IdData_json.content)
    return IdData

def divideAsAddress(IdData) :
    dd = {}
    for dict in IdData :
        if dd.get(dict['campus']) == None :
            dd[dict['campus']]={}
        if dd[dict['campus']].get(dict['building']) == None :
            dd[dict['campus']][dict['building']]={}
        if dd[dict['campus']][dict['building']].get(dict['floor']) == None :
            dd[dict['campus']][dict['building']][dict['floor']]={}
        if dd[dict['campus']][dict['building']][dict['floor']].get(dict['room']) == None :
            dd[dict['campus']][dict['building']][dict['floor']][dict['room']]=[]
        dd[dict['campus']][dict['building']][dict['floor']][dict['room']].append(dict)
    return dd

def query(s:str,dd):
    args=s.split()
    if args[0] == '学' :
        campus = '学院路校区'
    if args[0] == '沙' :
        campus = '沙河校区'
        building = '沙河' + args[1][0] + '号公寓' + args[1][1] + '楼'
        floor = args[2][0]
        room = args[2]
    try:
        res = dd[campus][building][floor][room]
    except KeyError :
        print('未找到电表，请检查输入。')
        return 
    except UnboundLocalError :
        print('未找到电表，请检查输入。')
        return 
    for meter in res :
        print('电表地址:%s' % meter['address'])
        queryByID(meter['identityNo'])
sqlQueryMeter='select * \
from IDDATA \
where \
CAMPUS="%s" \
and \
BUILDING="%s" \
and \
ROOM="%s" \
;'
class database(): # TODO: Check input validity
    
    def __init__(self):
        self.d = sqlite3.connect('data.sqlite3')
        if(self.d.execute("select count(*) from sqlite_master where type='table' and name='IDDATA'").fetchone()[0] == 0):
            self.d.execute("create table IDDATA(ID INT PRIMARY KEY NOT NULL, IDENTITYNO text not null, NAME TEXT, ADDRESS TEXT, METERNO TEXT, CAMPUS TEXT, BUILDING TEXT, FLOOR TEXT, ROOM TEXT);")
        if(self.d.execute("select count(*) from sqlite_master where type='table' and name='USAGE' ").fetchone()[0] == 0):
            self.d.execute("create table USAGE(ID int primary key not null, DATE text not null, USAGE text, REMAINING text);")
        return
    def updateIdData(self):
        self.d.execute('delete from IDDATA;') # Clear old data
        data = getIdData()
        for i in data:
            self.d.execute('insert into IDDATA values (%d,"%s","%s","%s","%s","%s","%s","%s","%s");'% (\
                           i['id'], \
                           i['identityNo'], \
                           i['name'], \
                           i['address'], \
                           i['meterNo'], \
                           i['campus'], \
                           i['building'], \
                           i['floor'], \
                           i['room']))
        self.d.commit()
        return
    def updateUsageData(self,mid):
        mit=(int)mid
        p = myParser()
        yesterday=datetime.date.today()-datetime.timedelta(days=1)
        yesterday=str(yesterday)
        url = "http://shsd.buaa.edu.cn/PubBuaa"
        req = requests.get(url, {'id':mid})
        p.feed(req.text)
        #TODO:catch AttributeError
        self.d.execute('insert into USAGE values (%d,"%s","%s","%s")'%(mid,yesterday,p.yesterday_usage,p.remain))
        return
    def queryMeterId(self,id=None,name=None,campus=None,building=None,floor=None,room=None):
        d=self.d
        if(campus == None):
            return d.execute('select distinct CAMPUS from IDDATA;').fetchall()
        if(building == None):
            return d.execute(' select distinct BUILDING from IDDATA where CAMPUS="%s"'%campus).fetchall()
        if(floor == None and room == None):
            return d.execute('select distinct FLOOR from IDDATA where CAMPUS="%s" and BUILDING="%s";' % (campus,building)).fetchall()
        if(room  == None):
            return d.execute('select distinct FLOOR from IDDATA where CAMPUS="%s" and BUILDING="%s" and FLOOR="%s";' % (campus,building,floor)).fetchall()
        return d.execute('select * from IDDATA where CAMPUS="%s" and BUILDING="%s" and ROOM="%s";' %(campus,building,room)).fetchall()
    def queryMeterUsage(id):
        return
'''   
queryByID("44210")
queryByID("44569")
idDataSet = divideAsAddress(getIdData())
while(1):
    q = input()
    query(q,idDataSet)
'''

'''
    id = input()
    if id == 'A':
        id = "44210"
    if id == 'B':
        id = "44569"
    queryByID(id)
'''
