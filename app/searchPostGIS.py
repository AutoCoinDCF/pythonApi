from flask import Flask,request
#from app import app
import psycopg2
import ..database.postGIS.PGOperation import PGO

app = Flask(__name__)
@app.route('/searchLocationName/')
def searchLocationName():
    conn = psycopg2.connect(database="qbsys_geo", user="postgres", password="example", host="10.60.1.142", port="5432")
    cur = conn.cursor() 
    cur.execute("SELECT geom FROM world_states_provinces WHERE name = 'Qinghai';")
    rows=cur.fetchall()
    for row in rows:

        return("geometry = "+ str(row[0]))
        #return('id='+str(row[0])+ ',name='+str(row[1])+',pwd='+str(row[2])+',singal='+str(row[3])+'\n')

    cur.close()
    conn.close()




if __name__ == '__main__':
    app.run()

