from database.mongoDB import MGO

def createIndex():

    """ config=[
        {'host':'10.60.1.140', 'port':6080, 'user':'root', 'pwd':'111111', 'dbname':'GlobalTerroris', 'collName':'QBEvents'},
        {'host':'10.60.1.140', 'port':6080, 'user':'root', 'pwd':'111111', 'dbname':'humanEventGraph', 'collName':'eventData'},
        {'host':'10.60.1.140', 'port':6080, 'user':'root', 'pwd':'111111', 'dbname':'wikidata', 'collName':'Coordinate'}
        ] """
    db = MGO.connectMG('10.60.1.140',6080,'root','111111','humanEventGraph')
    #db.Coordinate.create_index({"location" : "2dsphere"})
    db.eventData.create_index( [('location_list[0].geometry' , "2dsphere" )] )



if __name__ == '__main__':
    createIndex()
