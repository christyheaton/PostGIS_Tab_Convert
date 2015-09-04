'''
This script turns all of the tables in a list of postgis databases into MapInfo Tab files based on a query.
It must be run in the QGIS environment. Tested in QGIS 2.8.1.
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
    print "Connection to", server, database, "established."

    # go through every table in the list and turn it into a vector layer
    for table in tableList:
        print "Conection to", database, ": ", table, " established."
        uri.setDataSource("public", table, "way")
        vlayer = QgsVectorLayer(uri.uri(), table, "postgres")

        # get row and column counts and print them out
        if table == "planet_osm_line":
            fields = vlayer.pendingFields()
            numFields = len(fields)
            numRows = vlayer.featureCount()

            print "Original", database, ": ", table, "has", str(numRows), "rows and", str(numFields), "columns."

            railway = ["Railway", r""""railway" != ''"""]
            request = QgsFeatureRequest()
            request.setFilterExpression(railway[1])
            
            selectedRows = []
            selectedFeatures = vlayer.getFeatures(request)
            for feature in selectedFeatures:
                selectedRows.append(feature.id())
            vlayer.setSelectedFeatures(selectedRows)

            #turn tables into tab files
            output = outputBase + "/" + railway[0] + "_" + database + ".tab"
            #dataFile = outputBase + database + "/" + table + ".dbf"
            # export selection as TAB
            QgsVectorFileWriter.writeAsVectorFormat(vlayer, output, encoding, coordsys, "MapInfo File", True)
            print "Translation of " + railway[0] + "_" + database + ".tab successful."
        
        # doesn't work yet - need queries    
        elif table == "planet_osm_point":
            fields = vlayer.pendingFields()
            numFields = len(fields)
            numRows = vlayer.featureCount()

            #pointQuery = NEED QUERY
            print "Original", database, ": ", table, "has", str(numRows), "rows and", str(numFields), "columns."

            #request = QgsFeatureRequest()
            #request.setFilterExpression(pointQuery)
                        
            #selectedRows = []
            #selectedFeatures = vlayer.getFeatures(request)
            #for feature in selectedFeatures:
            #    selectedRows.append(feature.id())
            #vlayer.setSelectedFeatures(selectedRows)

            #turn tables into shapefiles
            output = outputBase + database + "/" + table + ".shp"
            #dataFile = outputBase + database + "/" + table + ".dbf"
            # export selection as TAB
            QgsVectorFileWriter.writeAsVectorFormat(vlayer, output, encoding, coordsys, "ESRI Shapefile", False)
            print "Translation of " + database + ": " + table + ".shp successful."

        elif table == "planet_osm_polygon":
            fields = vlayer.pendingFields()
            numFields = len(fields)
            numRows = vlayer.featureCount()

            print "Original", database, ": ", table, "has", str(numRows), "rows and", str(numFields), "columns."

            states = ["States", r"""("boundary" != '' and "admin_level"='4') or ("place" like '%state%' or "place" like '%province%')"""]
            counties = ["Counties", r""""boundary" <> '' and ("admin_level" = '6' or "place" = 'county')"""]
            urbanAreas = ["UrbanAreas", r"""("boundary" != '' and ("admin_level"='7' or "admin_level" = '8')) or ("place" like '%city%' or "place" like '%municipality%')"""]
            water = ["Water", r""""natural" like '%bay%' or  "natural" like '%water%' or  "landuse" = 'reservoir'"""]
            majorParks = ["MajorParks", r""""boundary" in ('national_park')"""]
            landuse = ["Landuse", r""""landuse" in ('forest','recreation_ground','railway','military') or "boundary" = 'protected_area' or "military" <> '' or "railway" = 'station' or "leisure" = 'park'"""]
            airports = ["Airports", r""""aeroway"<>''"""]

            polygons = [states, counties, urbanAreas, water, majorParks, landuse, airports]

            for polygon in polygons:
                request = QgsFeatureRequest()
                request.setFilterExpression(polygon[1])
            
                selectedRows = []
                selectedFeatures = vlayer.getFeatures(request)
                for feature in selectedFeatures:
                    selectedRows.append(feature.id())
                vlayer.setSelectedFeatures(selectedRows)

                #turn tables into tab files
                output = outputBase + "/" + polygon[0] + "_" + database + ".tab"
                # export selection as TAB
                QgsVectorFileWriter.writeAsVectorFormat(vlayer, output, encoding, coordsys, "MapInfo File", True)
                print "Translation of " + polygon[0] + "_" + database + ".tab successful."

        elif table == "planet_osm_roads":
            fields = vlayer.pendingFields()
            numFields = len(fields)
            numRows = vlayer.featureCount() 
            
            print "Original", database, ": ", table, "has", str(numRows), "rows and", str(numFields), "columns."

            # lists of road names and queries
            expressway = ["Expressways", r""""highway" like '%motorway%' or  "highway" like '%trunk%'"""]
            primaryHighway = ["PrimaryHighway", r""""highway" = 'primary'"""]
            secondaryHighway = ["SecondaryHighway", r""""highway" = 'secondary'"""]
            regionalHighway = ["RegionalHighway", r""""highway" = 'tertiary'"""]
            localRoutes = ["LocalRoutes", r""""highway" = 'unclassified'"""]
            streets = ["Streets", r""""highway" like '%residential%' or  "highway" like '%service%'"""]

            roads = [expressway, primaryHighway, secondaryHighway, regionalHighway, localRoutes, streets]

            for road in roads:                        
                request = QgsFeatureRequest()
                request.setFilterExpression(road[1])
            
                selectedRows = []
                selectedFeatures = vlayer.getFeatures(request)
                for feature in selectedFeatures:
                    selectedRows.append(feature.id())
                vlayer.setSelectedFeatures(selectedRows)

                #turn tables into tab files
                output = outputBase + "/" + road[0] + "_" + database + ".tab"
                # export selection as TAB
                QgsVectorFileWriter.writeAsVectorFormat(vlayer, output, encoding, coordsys, "MapInfo File", True)
                print "Translation of " + road[0] + "_" + database + ".tab successful."

        else:
            print "Bad table name."

print "Process complete."
