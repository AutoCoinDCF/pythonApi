from flask import Flask,request
#from app import app
import pymongo
from pymongo import MongoClient,GEO2D

app = Flask(__name__)
@app.route('/searchPoints/',methods=['POST'])
def searchPoints():
    mydb = MongoClient('mongodb://localhost:27017/').test
    mydb.eventTest.create_index( [('location' , "2dsphere" )] )
    r = mydb.eventTest.find_one({'locationName': "1"}) 
    return r['locationName']
    """ if request.method == 'GET':
        return 'get'
    else:
        return 'post' """



if __name__ == '__main__':
    app.run()

