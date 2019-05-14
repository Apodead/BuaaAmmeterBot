import sqlite3
import pydblite
import datetime
import crawler

dbFileName = 'data.sqlite3'
d = sqlite3.connect(dbFileName, check_same_thread=False) # Warning: Check thread safety
def table_exist(table):
    return d.execute("select count(*) "\
        "from sqlite_master "\
        "where type='table'"\
        "and name='%s'"\
        %(table)\
        ).fetchone()[0]
if not table_exist("IDDATA"):
    d.execute("create table IDDATA("\
            "ID INT PRIMARY KEY NOT NULL, "\
            "IDENTITYNO text not null, "\
            "NAME TEXT, "\
            "ADDRESS TEXT, "\
            "METERNO TEXT, "\
            "CAMPUS TEXT, "\
            "BUILDING TEXT, "\
            "FLOOR TEXT, "\
            "ROOM TEXT);")
if not table_exist("USAGE"):
    d.execute("create table USAGE("\
            "KEY text not null, "\
            "ID int not null, "\
            "DATE text not null, "\
            "USAGE text, "\
            "REMAINING text);")
d.commit()
def updateIdData():
    d.execute('delete from IDDATA;') # Clear old data
    data = crawler.getIdData()
    for i in data:
        d.execute('insert into IDDATA values (%d,"%s","%s","%s","%s","%s","%s","%s","%s");'% (\
                       i['id'], \
                       i['identityNo'], \
                       i['name'], \
                       i['address'], \
                       i['meterNo'], \
                       i['campus'], \
                       i['building'], \
                       i['floor'], \
                       i['room']))
    d.commit()
    return
def queryMeterId(id=None,name=None,campus=None,building=None,floor=None,room=None):
    table='IDDATA'
    target=''
    condition=''
    def add_condition(**kwargs):
        nonlocal condition
        for i in kwargs.items():
            print(i)
            if(condition != ''):
                condition += ' and'
            condition += ' {0[0]}="{0[1]}"'.format(i)
    if(campus != None):
        add_condition(CAMPUS=campus)
    if(building != None):
        add_condition(BUILDING=building)
    elif(floor != None):
        add_condition(FLOOR=floor)
    if(room != None):
        add_condition(ROOM=room)
    if condition != '' : condition = 'where' + condition
    target = 'ID'
    sql = 'select distinct {} from {} {};'.format(target,table,condition)
    print(sql)
    return [i[0] for i in d.execute(sql).fetchall()]
def queryCampus():
    sql = 'select distinct CAMPUS from IDDATA;'
    return [i[0] for i in d.execute(sql).fetchall()]
def queryBuildings(campus):
    sql = 'select distinct BUILDING from IDDATA '\
          'where CAMPUS="{}";'.format(campus)
    print(sql)
    return [i[0] for i in d.execute(sql).fetchall()]
def queryFloors(campus, building):
    sql = 'select distinct FLOOR from IDDATA '\
          'where CAMPUS="{}" and BUILDING="{}";'\
          .format(campus, building)
    return [i[0] for i in d.execute(sql).fetchall()]
def queryRooms(campus, building, floor):
    sql = 'select distinct ROOM from IDDATA '\
          'where CAMPUS="{}" and BUILDING="{}" '\
          'and FLOOR="{}";'.format(campus, building, floor)
    return [i[0] for i in d.execute(sql).fetchall()]
def queryMeters(campus, building, floor, room):
    sql = 'select * from IDDATA '\
          'where CAMPUS="{}" and BUILDING="{}" '\
          'and FLOOR="{}" and ROOM="{}";'.format\
          (campus, building, floor, room)
    return [i[4] for i in d.execute(sql).fetchall()]
def queryMeterInfo(mid):
    sql = 'select * from IDDATA '\
          'where ID={};'.format(mid)
    return d.execute(sql).fetchone()
def updateUsageData(mid):
    mid=int(mid)
    yesterday=datetime.date.today()-datetime.timedelta(days=1)
    yesterday=str(yesterday)
    key = str(mid) + yesterday
    rem,yst,his,tpu=crawler.query_usage(mid)
    if(d.execute('select count(*) from USAGE where KEY="{}";'.format(key)).fetchall()[0][0] == 0):
        d.execute('insert into USAGE values ("%s",%d,"%s","%s","%s")'%(key,mid,yesterday,yst,rem))
        d.commit()
    return
def queryMetersUsage(ids):
    print('test')
    if type(ids) is not list:
        ids = [ids]
    for i in ids:
        sql = 'select * from USAGE where ID={}'.format(i)
        print( d.execute(sql).fetchall())
    return
