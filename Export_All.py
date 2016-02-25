'''
This script turns all of the tables in a list of postgis databases into shapefiles.
It must be run in the QGIS environment. Tested in QGIS 2.8.1.
This script converts without considering size or breaking up files in to smaller chunks.
'''

# create databases list and table list
databases = ["AQ", "AR", "BR", "CA", "CL", "CR", "CU", "DE", "ES", "GB", "GT", "JP", "KR", "MX", "NG", "NI", "PA", "RU", "SV"]
print "Databases:", databases
tableList = ["planet_osm_line", "planet_osm_point", "planet_osm_polygon", "planet_osm_roads"]
print "Table list:", tableList

# create other variables
server = "myServer"
encoding = "utf-8"
coordsys = QgsCoordinateReferenceSystem(3395, QgsCoordinateReferenceSystem.EpsgCrsId)
outputBase = "C:/Temp/"

# connect to server
uri = QgsDataSourceURI()
for database in databases:
    uri.setConnection(server, "5432", database, "username", "password")
    print "Connection to " + server + " " + database + " established."

    # go through every table in the list and turn it into a vector layer
    for table in tableList:
        uri.setDataSource("public", table, "way")
        print "Conection to " + database + ": " + table + " established."
        vlayer = QgsVectorLayer(uri.uri(), table, "postgres")

        # get row and column counts and print
        fields = vlayer.pendingFields()
        numFields = len(fields)
        rows = vlayer.featureCount() 
        print database + ": " + table + " has " + str(rows) + " rows and " + str(numFields) + " columns."

        # turn into shapefile.
        output = outputBase + database + "/" + table + ".shp"
        QgsVectorFileWriter.writeAsVectorFormat(vlayer, output, encoding, coordsys, "ESRI Shapefile")
        print "Translation of " + database + ": " + table + ".shp successful."

print "Process complete."
