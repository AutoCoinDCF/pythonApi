from flask import Flask,request
from flask_cors import CORS
#from app import app
import psycopg2
from database.postGIS import PGO
from database.mongoDB import MGO
import json
from bson.objectid import ObjectId
import urllib
from mapGraph.BezierLine import BezierLine as BL

app = Flask(__name__)
CORS(app,  resources={r"/*": {"origins": "*"}})   # 允许所有域名跨域
#cors = CORS(app, resources={r"/.*": {"origins": "http://192.168.1.92:8081"}})   # 只允许特定域名跨域

@app.route('/searchLocationName/<localName>')
def searchLocationName(localName):
    pg = PGO()
    if(PGO.is_Chinese(localName)):
        rows_countries = pg.select(r"SELECT id,country FROM world_states_countries WHERE country ~* '%s';" %(localName))
        rows_provinces = pg.select(r"SELECT objectid,enname FROM world_states_provinces WHERE enname ~* '%s';" %(localName))
    else:
        rows_countries = pg.select(r"SELECT id,enname FROM world_states_countries WHERE enname ~* '%s';" %(localName))
        rows_provinces = pg.select(r"SELECT objectid,name FROM world_states_provinces WHERE name ~* '%s';" %(localName))

    suitableLocations = []
    """ suitableLocationO = {} """
    if(rows_provinces == None and rows_countries == None):
        return 'false'
    else:
        if(rows_provinces != None):
            for row in rows_provinces:
                locN = {
                    "id":row[0],
                    "name":row[1],
                    "type":'province'
                }
                suitableLocations.append(locN)
        if(rows_countries != None):
            for row in rows_countries:
                locN = {
                    "id":row[0],
                    "name":row[1].strip(),
                    "type":'country'
                }
                suitableLocations.append(locN)
        data = {
            "code":0,
            "data":suitableLocations
        }
        return json.dumps(data)



@app.route('/searchAreaByIds/',methods=['POST'])
def searchAreaByIds():
    config = [
        {"tableName":'world_states_countries',"idSign":"world_states_countries_postgis","IdField":"id","queryFields":['id','country','enname'],"type":"country"},
        {"tableName":'world_states_provinces',"idSign":"world_states_provinces_postgis","IdField":"objectid","queryFields":['objectid','name','enname'],"type":"province"}]
    pg = PGO()
    ids = request.json['ids']
    suitableLocations = []
    for cf in config:
        sids = ",".join([str(id.split(".")[1]) for id in ids if id.split(".")[0] == cf['idSign']])
        queryFields = ",".join(cf['queryFields'])
        sql =  "SELECT " + queryFields + " FROM " + cf['tableName'] +" WHERE " + cf['IdField'] + " in (" + sids + ")"
        rows = pg.select(sql)
        if(rows != None):
            for row in rows:
                name = ''
                if row[1] == None:
                    name = row[2]
                else:
                    name = row[1]
                locN = {
                    "id":cf['type']  + "." + str(row[0]),
                    "name":name.strip(),
                    "type":cf['type']
                }
                suitableLocations.append(locN)
    data = {
        "code":0,
        "data":suitableLocations
    }
    return json.dumps(data)
    


""" @app.route('/translation_youdao/',methods=['GET'])
def translation_youdaoAPI():
    pg = PGO()
    rows = pg.select(r"SELECT country,enname FROM world_states_countries;")
    #suitableLocations = []
    for row in rows:
        if(row[0] != None and (row[1] == None or row[1] == 'a')):
            oname = row[0].replace("'",'')
            dic = {'i':oname}
            encStr = urllib.parse.urlencode(dic)
            response = urllib.request.urlopen('http://fanyi.youdao.com/translate?&doctype=json&type=AUTO&' + encStr)
            try:
                translateStr = json.loads(response.read().decode('utf-8').replace('\n','').lstrip())['translateResult'][0][0]['tgt']#response.read().translateResult[0][0].tgt
                pg.updata(r"UPDATE world_states_countries SET enname='%s'  WHERE country = '%s';"%(translateStr,oname))
            except:
                print('结束')
                return '结束' """


@app.route('/exploreOrg/',methods=['POST'])
def exploreOrg():
    mg = MGO(user='root', pwd='111111')
    collName = 'Coordinate'#'Organization'
    geometryStrArr = request.json['geometry']
    findOrArr = []
    for geometryStr in geometryStrArr:
        geometryObj = json.loads(geometryStr)
        findO = {"location":{"$within":{"$geometry":geometryObj}}}
        findOrArr.append(findO)
    findObj = {'$or':findOrArr}
    #findObj = {"Entity_id":'Q1065'}
    rows = mg.find(collName,findObj)
    features=[]
    Location = {}
    for row in rows:
        X = str(row['location']['coordinates'][0]) 
        Y = str(row['location']['coordinates'][1])
        ident = X + Y
        Org = {
            "OrgName":row['Entity_name'],
            "id":"org&" + row['Entity_id'],
        }
        location = row['location']
        if(ident in Location):
            OrgArr = Location[ident]['Orgs']
            OrgArr.append(Org)
        else:
            Location[ident] = {
                "Orgs":[Org],
                "location":location
            }

    for k,v in Location.items():
        location = v['location']
        featureId = k
        orgs = v['Orgs']
        feature = {
            "type": "Feature",
			"id":"org&" + featureId,
			"geometry": location,
			"properties": {
                'Params':orgs,
                'selectedNum':len(orgs)
            }
        }
        features.append(feature)
    data = {
        "code":0,
        "data":{
            'Features':{ 
                "type": "FeatureCollection",
                'crs': {
                    'type': 'name',
                    'properties': {
                        'name': 'EPSG:4326'
                    }
                },
                "features": features
            }
        }
    }
    return json.dumps(data)

@app.route('/exploreEvent/',methods=['POST'])
def exploreEvent():
    config=[
        {'host':'10.60.1.140', 'port':6080, 'user':'root', 'pwd':'111111', 'dbname':'GlobalTerroris', 'collName':'QBEvents'},
        {'host':'10.60.1.140', 'port':6080, 'user':'root', 'pwd':'111111', 'dbname':'humanEventGraph', 'collName':'eventData'}
        ]
    features=[]
    Location = {}
    allrows = []
    for cf in config:
        mg = MGO(host=cf['host'], port=cf['port'], user=cf['user'], pwd=cf['pwd'],dbname=cf['dbname'])
        collName = cf['collName']
        geometryStrArr = request.json['geometry']
        findOrArr = []
        for geometryStr in geometryStrArr:
            geometryObj = json.loads(geometryStr)
            #findO_line = {"location_list.from.geometry":{"$within":{"$geometry":geometryObj}}}
            findO_fromLine = {"location_list.from":{'$elemMatch':{'geometry':{"$within":{"$geometry":geometryObj}}}}}
            findO_toLine = {"location_list.to":{'$elemMatch':{'geometry':{"$within":{"$geometry":geometryObj}}}}}
            findO_point = {"location_list.geometry":{"$within":{"$geometry":geometryObj}}}
            findOrArr.append(findO_fromLine)
            findOrArr.append(findO_toLine)
            findOrArr.append(findO_point)
        findObj = {'$or':findOrArr}
        #findObj = {"Entity_id":'Q1065'}
        rows = mg.find(collName,findObj)
        for row in rows:
            allrows.append(row)
    
    
    for row in allrows:
            
        if 'from' in row['location_list'][0].keys():
            froms = row['location_list'][0]['from']
            tos = row['location_list'][0]['to']
            locallineName = '线事件'
            EventId = row['_id']
            linesGeometry = []
            linesName = []
            i = 0
            completeEvent = ''
            eventType = row['event_subtype']
            while i < len(froms):
                fromName = froms[i]['name']
                toName = tos[i]['name']
                fromCoor = froms[i]['geometry']['coordinates']
                toCoor = tos[i]['geometry']['coordinates']
                bl = BL(fromCoor,toCoor,50)
                lineGeometry = bl.getBezierPoints()
                lineName = [fromName,toName]
                linesGeometry.append(lineGeometry)
                linesName.append(lineName)
                i = i + 1
            feature = {
                "type": "Feature",
                "id":"event&" + EventId,
                "geometry": {"type": "MultiLineString","coordinates":linesGeometry},
                "properties": {
                    'Params':[{'id':"event&" + EventId,'time':'','completeEvent':completeEvent}],
                    'selectedNum':1,
                    'locationName':locallineName
                }
            }
            features.append(feature)
        else:
            EventId = str(row['_id'])
            localName = row['location_list'][0]['name']
            pointGeometry = row['location_list'][0]['geometry']
            X = str(pointGeometry['coordinates'][0]) 
            Y = str(pointGeometry['coordinates'][1])
            ident = X + Y      
            eventType = row['event_subtype']
            completeEvent = ''
            time = ''
            Event = {
                "completeEvent":completeEvent,
                "id":"event&" + EventId,
                'time':time,
                'eventType':eventType
            }
            location = row['location_list'][0]['geometry']
            if(ident in Location):
                EventArr = Location[ident]['Events']
                EventArr.append(Event)
            else:
                Location[ident] = {
                    "Events":[Event],
                    "location":location
                }

    for k,v in Location.items():
        location = v['location']
        featureId = k
        events = v['Events']
        feature = {
            "type": "Feature",
            "id":"event&" + featureId,
            "geometry": location,
            "properties": {
                'Params':events,
                'locationName':localName,
                'selectedNum':len(events)
            }
        }
        features.append(feature)
    data = {
        "code":0,
        "data":{
            'Features':{ 
                "type": "FeatureCollection",
                'crs': {
                    'type': 'name',
                    'properties': {
                        'name': 'EPSG:4326'
                    }
                },
                "features": features
            }
        }
    }
    return json.dumps(data)


def getGeometryBySearRes(row):
    geometry = {}
    if "Entity_id" in row:
        geometry = row['location']
    else:
        if 'from' in row['location_list'][0].keys():
            froms = row['location_list'][0]['from']
            tos = row['location_list'][0]['to']
            linesGeometry = []
            i = 0
            while i < len(froms):
                fromName = froms[i]['name']
                toName = tos[i]['name']
                fromCoor = froms[i]['geometry']['coordinates']
                toCoor = tos[i]['geometry']['coordinates']
                bl = BL(fromCoor,toCoor,50)
                lineGeometry = bl.getBezierPoints()
                linesGeometry.append(lineGeometry)
                i = i + 1
            geometry = {"type": "MultiLineString","coordinates":linesGeometry}
        else:
            geometry = row['location_list'][0]['geometry']
    return geometry


def getIdentBySearRes(row):
    ident = ''
    if "Entity_id" in row:
        X = str(row['location']['coordinates'][0]) 
        Y = str(row['location']['coordinates'][1])
        ident = 'org&' + X + Y
    else:
        if 'from' in row['location_list'][0].keys():
            ident = 'event&' + str(row["_id"])
        else:
            X = str(row['location_list'][0]['geometry']['coordinates'][0]) 
            Y = str(row['location_list'][0]['geometry']['coordinates'][1])
            ident = 'event&' + X + Y
    return ident

def getEventDictBySearRes(row,dicto):   #根据一条查询结果生成事件特定格式的字典
    EventId = str(row['_id'])
    ident = getIdentBySearRes(row)
    eventType = row['event_subtype']
    Event = {
        "id":"event&" + EventId,
        'eventType':eventType
    }
    location = getGeometryBySearRes(row)
    
    if(ident in dicto):
        EventArr = dicto[ident]['Params']
        EventArr.append(Event)
    else:
        dicto[ident] = {
            "Params":[Event],
            "location":location
        }

def getOrgDictBySearRes(row,dicto):
    ident = getIdentBySearRes(row)
    Org = {
        "OrgName":row['Entity_name'],
        "id":"org&" + row['Entity_id'],
    }
    location = getGeometryBySearRes(row)
    if(ident in dicto):
        OrgArr = dicto[ident]['Params']
        OrgArr.append(Org)
    else:
        dicto[ident] = {
            "Params":[Org],
            "location":location
        }

@app.route('/getParamsByIds/',methods=['POST'])
def getParamsByIds():
    config=[
        {'host':'10.60.1.140', 'port':6080, 'user':'root', 'pwd':'111111', 'dbname':'GlobalTerroris', 'collName':'QBEvents'},
        {'host':'10.60.1.140', 'port':6080, 'user':'root', 'pwd':'111111', 'dbname':'humanEventGraph', 'collName':'eventData'},
        {'host':'10.60.1.140', 'port':6080, 'user':'root', 'pwd':'111111', 'dbname':'wikidata', 'collName':'Coordinate'}
        ]
    features=[]
    Location = {}
    allrows = []
    for cf in config:
        mg = MGO(host=cf['host'], port=cf['port'], user=cf['user'], pwd=cf['pwd'],dbname=cf['dbname'])
        collName = cf['collName']
        ids = request.json['ids']
        findOrArr = []
        for id in ids:
            findO = {}
            if len(id) < 20:
                findO = {"Entity_id":id}
            else:
                if "_" in  id:
                    findO = {"_id":id}
                else:
                    findO = {"_id":ObjectId(id)}
            findOrArr.append(findO)
        findObj = {'$or':findOrArr}
        rows = mg.find(collName,findObj)
        for row in rows:
            allrows.append(row)
    
    for row in allrows:
        
        if 'Entity_id' in row:
            getOrgDictBySearRes(row,Location)
        else:
            if len(row['location_list']) == 0 :
                continue
            getEventDictBySearRes(row,Location)

    for k,v in Location.items():
        location = v['location']
        featureId = k
        params = v['Params']
        feature = {
            "type": "Feature",
            "id":featureId,
            "geometry": location,
            "properties": {
                'Params':params,
                'selectedNum':len(params)
            }
        }
        features.append(feature)
    data = {
        "code":0,
        "data":{
            'Features':{ 
                "type": "FeatureCollection",
                'crs': {
                    'type': 'name',
                    'properties': {
                        'name': 'EPSG:4326'
                    }
                },
                "features": features
            }
        }
    }
    return json.dumps(data)

@app.route('/getEventByIds/',methods=['POST'])
def getEventByIds():
    config=[
        {'host':'10.60.1.140', 'port':6080, 'user':'root', 'pwd':'111111', 'dbname':'GlobalTerroris', 'collName':'QBEvents'},
        {'host':'10.60.1.140', 'port':6080, 'user':'root', 'pwd':'111111', 'dbname':'humanEventGraph', 'collName':'eventData'}
        ]
    features=[]
    Location = {}
    allrows = []
    for cf in config:
        mg = MGO(host=cf['host'], port=cf['port'], user=cf['user'], pwd=cf['pwd'],dbname=cf['dbname'])
        collName = cf['collName']
        ids = request.json['ids']
        findOrArr = []
        for id in ids:
            findO = {"_id":id}
            findOrArr.append(findO)
        findObj = {'$or':findOrArr}
        rows = mg.find(collName,findObj)
        for row in rows:
            allrows.append(row)
    
    for row in allrows:
        if len(row['location_list']) == 0 :
            continue
        if 'from' in row['location_list'][0].keys():
            froms = row['location_list'][0]['from']
            tos = row['location_list'][0]['to']
            locallineName = '线事件'
            EventId = row['_id']
            linesGeometry = []
            linesName = []
            i = 0
            completeEvent = ''
            eventType = row['event_subtype']
            while i < len(froms):
                fromName = froms[i]['name']
                toName = tos[i]['name']
                fromCoor = froms[i]['geometry']['coordinates']
                toCoor = tos[i]['geometry']['coordinates']
                bl = BL(fromCoor,toCoor,50)
                lineGeometry = bl.getBezierPoints()
                lineName = [fromName,toName]
                linesGeometry.append(lineGeometry)
                linesName.append(lineName)
                i = i + 1
            feature = {
                "type": "Feature",
                "id":"event&" + EventId,
                "geometry": {"type": "MultiLineString","coordinates":linesGeometry},
                "properties": {
                    'Params':[{'id':"event&" + EventId,'time':'','completeEvent':completeEvent}],
                    'locationName':locallineName,
                    'selectedNum':1
                }
            }
            features.append(feature)
        else:
            EventId = row['_id']
            pointGeometry = row['location_list'][0]['geometry']
            localName = row['location_list'][0]['name']
            X = str(pointGeometry['coordinates'][0]) 
            Y = str(pointGeometry['coordinates'][1])
            ident = X + Y
            arguments = row['argument_list']
            
            eventType = row['event_subtype']
            relatedEntities = []
            completeEvent = ''
            content = row['event_content']
            time = ''
            

            Event = {
                "completeEvent":completeEvent,
                "id":"event&" + EventId,
                'time':time,
                'eventType':eventType
            }
            location = row['location_list'][0]['geometry']
            if(ident in Location):
                EventArr = Location[ident]['Events']
                EventArr.append(Event)
            else:
                Location[ident] = {
                    "Events":[Event],
                    "location":location
                }

    for k,v in Location.items():
        location = v['location']
        featureId = k
        events = v['Events']
        feature = {
            "type": "Feature",
            "id":"event&" + featureId,
            "geometry": location,
            "properties": {
                'Params':events,
                'locationName':localName,
                'selectedNum':len(events)
            }
        }
        features.append(feature)
    data = {
        "code":0,
        "data":{
            'Features':{ 
                "type": "FeatureCollection",
                'crs': {
                    'type': 'name',
                    'properties': {
                        'name': 'EPSG:4326'
                    }
                },
                "features": features
            }
        }
    }
    return json.dumps(data)

@app.route('/getOrgByIds/',methods=['POST'])
def getOrgByIds():
    mg = MGO(user='root', pwd='111111')
    collName = 'Coordinate'#'Organization'
    ids = request.json['ids']
    findOrArr = []
    for id in ids:
        #geometryObj = json.loads(geometryStr)
        findO = {"Entity_id":id}
        findOrArr.append(findO)
    findObj = {'$or':findOrArr}
    #findObj = {"Entity_id":'Q1065'}
    rows = mg.find(collName,findObj)
    features=[]
    Location = {}
    for row in rows:
        X = str(row['location']['coordinates'][0]) 
        Y = str(row['location']['coordinates'][1])
        ident = X + Y
        Org = {
            "OrgName":row['Entity_name'],
            "id":"org&" + row['Entity_id'],
        }
        location = row['location']
        if(ident in Location):
            OrgArr = Location[ident]['Orgs']
            OrgArr.append(Org)
        else:
            Location[ident] = {
                "Orgs":[Org],
                "location":location
            }

    for k,v in Location.items():
        location = v['location']
        featureId = k
        orgs = v['Orgs']
        feature = {
            "type": "Feature",
			"id":"org&" + featureId,
			"geometry": location,
			"properties": {
                'Params':orgs,
                'selectedNum':len(orgs)
            }
        }
        features.append(feature)
    data = {
        "code":0,
        "data":{
            'Features':{ 
                "type": "FeatureCollection",
                'crs': {
                    'type': 'name',
                    'properties': {
                        'name': 'EPSG:4326'
                    }
                },
                "features": features
            }
        }
    }
    return json.dumps(data)


@app.route('/node2GIS/',methods=['POST'])
def node2GIS():
    data = {
        "code": 0,
        "data": [{
            "eventGeoJson": {
                "type": "FeatureCollection",
                "crs": {
                    "type": "name",
                    "properties": {
                        "name": "EPSG:4326"
                    }
                },
                "features": [
                        {"type": "Feature",
                            "geometry": {
                            "type": "Point",
                            "id": "event_Feature_北京",
                            "coordinates": [116.3809433, 39.9236145]},
                            "properties": {
                            "Params": [{"id": "event_V104", "time": "2002-01-02"}, {"id": "event_V105", "time": "2018-01-03"},
                                {"id": "event_V102", "time": "2018-01-03"}],
                            "locationName": "北京",
                            "selectedNum": 3
                            }
                        },
                        {"type": "Feature",
                            "geometry": {
                            "type": "Point",
                            "id": "event_Feature_纽约",
                            "coordinates": [74.0060, 40.7128]},
                            "properties": {
                            "Params": [{"id": "event_V108", "time": "2002-02-02"}, {"id": "event_V109", "time": "2018-02-03"},
                                        {"id": "event_V120", "time": "2018-02-03"}],
                            "locationName": "纽约",
                            "selectedNum": 3
                            }
                        }
                    ]
                }
        }]
    }
    return json.dumps(data)

@app.route("/upload", methods=['post', 'get'])
def upload():
    f = request.files['file']
    print(f.filename)
    f.save(f.filename)

    """ image_file = Image.open(f.filename)  # open colour image
    image_file = image_file.convert('1')  # convert image to black and white
    path = './static/result.png' """
    """ image_file.save(path) """
    """ return 'http://localhost/static/result.png' """






if __name__ == '__main__':
    app.run()

