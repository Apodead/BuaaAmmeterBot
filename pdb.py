from pydblite import Base
import datetime
import crawler
import configure as conf

dbFileNameSuffix = conf.db_filename
idData = Base('id.'+dbFileNameSuffix)
if idData.exists():
    idData.open()
else:
    idData.create('id', 'name', 'meterNo', 'campus', \
                 'building', 'floor', 'room')
usageData = Base('usage.' + dbFileNameSuffix)
if usageData.exists():
    usageData.open()
else:
    usageData.create('id', 'date', 'usage', 'remain')

def updateIdData():
    #idData.execute('delete from IDDATA;') # Clear old data
    idData.delete(idData)
    data = crawler.getIdData()
    for i in data:
        idData.insert( i['id'], i['name'], i['meterNo'], i['campus'], \
                       i['building'], i['floor'], i['room'])
    idData.commit()
    return
def updateUsageData(mids):
    if type(mids) is int \
    or type(mids) is str:
        mids=[mids]
    for mid in mids:
        mit=int(mid)
        yesterday=datetime.date.today()-datetime.timedelta(days=1)
        yesterday=str(yesterday)
        rem,yst,his,tpu=crawler.query_usage(mid)
        usageData.insert(mid,yesterday,yst,rem)
    return
