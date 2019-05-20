import pymongo
from pymongo import MongoClient,GEO2D
#myclient = MongoClient('mongodb://localhost:27017/')
mydb = MongoClient('mongodb://localhost:27017/').test
#mydb = myclient['test']
#mycol = mydb["restaurants"]
#mydb.restaurants.create_index([("location",GEO2D)])
#mydb.neighborhoods.ensureIndex({ 'geometry': "2dsphere" })
#mycol.places.create_index([("geometry",GEO2D)])
""" result = mydb.places.insert_many([{"loc": [2, 5]},{"loc":[30, 5]},{"loc": [1, 2]},{"loc": [4, 4]}]) """
""" for doc in mydb.neighborhoods.find({ 'geometry': { '$geoIntersects': { '$geometry': { type: "Point", 'coordinates': [ -73.93414657, 40.82302903 ] } } } } ):
    print(str(doc)) """


""" mydb.places.create_index([("loc",GEO2D)])
for doc in mydb.places.find({"loc": {"$near": [1, 1]}}).limit(1):
    print(doc) """

#mydb.test1.insert({'name': "Central Park",'location': { 'type': "Point", 'coordinates': [ -73.97, 40.77 ] }})
#result = mydb.places.insert_many([{'name': "Central Park",'location': { 'type': "Point", 'coordinates': [ -73.97, 40.77 ] }}])

#mydb.test1.create_index([("location",GEO2D)])




{'location': {'coordinates': [-73.856077, 40.848447], 'type': 'Point'},'id':'v200','time':'2008-01-02','locationName':'1'}
{'location': {'coordinates': [-73.961704, 40.662942], 'type': 'Point'},'id':'v201','time':'2008-01-02','locationName':'2'}
{'location': {'coordinates': [-73.98241999999999, 40.579505], 'type': 'Point'},'id':'v202','time':'2008-01-02','locationName':'3'}
{'location': {'coordinates': [-73.97, 40.77],'type': 'Point'},'id':'v203','time':'2008-01-02','locationName':'4'} 
{'location': {'coordinates': [-73.856077, 40.848447], 'type': 'Point'},'id':'v204','time':'2008-01-02','locationName':'1'}
{'location': {'coordinates': [-73.961704, 40.662942], 'type': 'Point'},'id':'v205','time':'2008-01-02','locationName':'2'}
{'location': {'coordinates': [-73.98241999999999, 40.579505], 'type': 'Point'},'id':'v206','time':'2008-01-02','locationName':'3'}
{'location': {'coordinates': [-73.97, 40.77],'type': 'Point'},'id':'v207','time':'2008-01-02','locationName':'4'} 
{'location': {'coordinates': [-73.856077, 40.848447], 'type': 'Point'},'id':'v208','time':'2008-01-02','locationName':'1'}
{'location': {'coordinates': [-73.961704, 40.662942], 'type': 'Point'},'id':'v209','time':'2008-01-02','locationName':'2'}
{'location': {'coordinates': [-73.98241999999999, 40.579505], 'type': 'Point'},'id':'v210','time':'2008-01-02','locationName':'3'}
{'location': {'coordinates': [-73.97, 40.77],'type': 'Point'},'id':'v211','time':'2008-01-02','locationName':'4'} 
{'location': {'coordinates': [-73.856077, 40.848447], 'type': 'Point'},'id':'v212','time':'2008-01-02','locationName':'1'}
{'location': {'coordinates': [-73.961704, 40.662942], 'type': 'Point'},'id':'v213','time':'2008-01-02','locationName':'2'}
{'location': {'coordinates': [-73.98241999999999, 40.579505], 'type': 'Point'},'id':'v214','time':'2008-01-02','locationName':'3'}
{'location': {'coordinates': [-73.97, 40.77],'type': 'Point'},'id':'v215','time':'2008-01-02','locationName':'4'} 
{'location': {'coordinates': [-73.856077, 40.848447], 'type': 'Point'},'id':'v216','time':'2008-01-02','locationName':'1'}
{'location': {'coordinates': [-73.961704, 40.662942], 'type': 'Point'},'id':'v217','time':'2008-01-02','locationName':'2'}
{'location': {'coordinates': [-73.98241999999999, 40.579505], 'type': 'Point'},'id':'v218','time':'2008-01-02','locationName':'3'}
{'location': {'coordinates': [-73.97, 40.77],'type': 'Point'},'id':'v219','time':'2008-01-02','locationName':'4'} 
{'location': {'coordinates': [-73.856077, 40.848447], 'type': 'Point'},'id':'v220','time':'2008-01-02','locationName':'1'}
{'location': {'coordinates': [-73.961704, 40.662942], 'type': 'Point'},'id':'v221','time':'2008-01-02','locationName':'2'}
{'location': {'coordinates': [-73.98241999999999, 40.579505], 'type': 'Point'},'id':'v222','time':'2008-01-02','locationName':'3'}
{'location': {'coordinates': [-73.97, 40.77],'type': 'Point'},'id':'v223','time':'2008-01-02','locationName':'4'} 








mydb.test1.create_index( [('location' , "2dsphere" )] )
for doc in mydb.test1.find():
    print(doc)

#{ 'location': { '$near': { '$geometry': { 'type': "Point", 'coordinates': [ -73.93414657, 40.82302903 ] } } } } 
#.limit(1)
