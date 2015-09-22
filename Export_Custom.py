'''
This script turns all of the tables in a list of postgis databases into shp files based on a query.
It must be run in the QGIS environment. Tested in QGIS 2.8.1.
'''
import os
from time import strftime
from PyQt4.QtCore import QVariant
outputBase = r"C:/Temp/"
if not os.path.exists(outputBase):
    print "Invalid directory"
logfile = open(outputBase + "logfile.txt", "a+")

def logMessage():
    print strftime("%Y-%m-%d %H:%M:%S") + " " + message
    logfile.write(strftime("%Y-%m-%d %H:%M:%S") + " " + message)

def printCounts(layer, name):
    fields = layer.pendingFields()
    num_fields = len(fields)
    num_rows = layer.featureCount()
    message = name + ' has ' + str(num_rows) + ' rows and ' + str(num_fields) + ' columns.\n'
    print strftime("%Y-%m-%d %H:%M:%S") + " " + message
    logfile.write(strftime("%Y-%m-%d %H:%M:%S") + " " + message)

def writeFile():
    QgsVectorFileWriter.writeAsVectorFormat(mapLayer, output, encoding, coordsys, "MapInfo File", False)
    message = "Translation of " + name + ".tab successful.\n"
    print strftime("%Y-%m-%d %H:%M:%S") + " " + message
    logfile.write(strftime("%Y-%m-%d %H:%M:%S") + " " + message)

def getSize():
    dataFile = outputBase + name + ".dat"
    message = name + ".dat" + " size: " + str(float(os.path.getsize(dataFile))/1024) + " KB.\n"
    print strftime("%Y-%m-%d %H:%M:%S") + " " + message
    logfile.write(strftime("%Y-%m-%d %H:%M:%S") + " " + message)

message = "PostGIS_Tab_Convert.py started...\n"
logMessage()

message = "Output will go in individual country folders in " + outputBase + "\n"
logMessage()

# create databases list and table list
databases = ["AQ", "AR", "BR", "CA", "CL", "CR", "CU", "DE", "ES", "GB", "GT", "JP", "KR", "MX", "NG", "NI", "PA", "RU", "SV"]

message = "Databases:" + str(databases) + "\n"
logMessage()

# tables - the same for all databases
tableList = ["planet_osm_line", "planet_osm_point", "planet_osm_polygon", "planet_osm_roads"]

message = "Table list:" + str(tableList) + "\n"
logMessage()

# create other variables
server = "myServer"
encoding = "utf-8"
coordsys = QgsCoordinateReferenceSystem(3395, QgsCoordinateReferenceSystem.EpsgCrsId)

# connect to nico6
uri = QgsDataSourceURI()
for database in databases:
    uri.setConnection(server, "5432", database, "username", "password")
    
    message = "Connection to " + server + " " + database + " established.\n"
    logMessage()

    # go through every table in the list and turn it into a vector layer
    for table in tableList:
        message = "Connection to " + database + ": " + table + " established.\n"
        logMessage()
        uri.setDataSource("public", table, "way")
        vlayer = QgsVectorLayer(uri.uri(), table, "postgres")

        if table == "planet_osm_line":
            printCounts(vlayer, table)

            railway = ["Railway", r""""railway" != ''"""]
            request = QgsFeatureRequest()
            request.setFilterExpression(railway[1])

            rails = QgsVectorLayer("LineString?crs=epsg:3857", "rails", "memory")
            if not rails.isValid(): raise Exception("Failed to create memory layer")
            pr = rails.dataProvider()
            rails.startEditing()
            pr.addAttributes([QgsField("name", QVariant.String),QgsField("railway", QVariant.String)])

            selectedRows = []
            selectedFeatures = vlayer.getFeatures(request)

            for feature in selectedFeatures:
                selectedRows.append(feature.id())
                newFeature = QgsFeature()
                newFeature.setGeometry(feature.geometry())
                newFeature.setAttributes([feature.attribute("name"), feature.attribute("railway")])
                pr.addFeatures([newFeature])

            rails.commitChanges()
            rails.updateExtents()
            vlayer.setSelectedFeatures(selectedRows)
            rails.setSelectedFeatures(selectedRows)
            mapLayer = QgsMapLayerRegistry.instance().addMapLayer(rails)

            #turn tables into tab files
            name = database + "/" + railway[0]
            output = outputBase + name + ".tab"
            printCounts(mapLayer, name + ".tab")
            writeFile()
            getSize()

        elif table == "planet_osm_point":
            printCounts(vlayer, table)

            cities1 = ["Cities1", r"""place = 'city'"""]
            cities2 = ["Cities2", r"""place = 'suburb'"""]
            cities3 = ["Cities3", r"""place = 'town'"""]
            cities4 = ["Cities4", r"""place = 'village'"""]
            cities6 = ["Cities6", r"""place = 'neighborhood'"""]
            cities8 = ["Cities8", r"""place in ('locality','hamlet')"""]
            stateLabels = ["StateLabels", r"""place in ('state','province')"""]
            
            points = [cities1, cities2, cities3, cities4, cities6, cities8, stateLabels]

            for point in points:
                request = QgsFeatureRequest()
                request.setFilterExpression(point[1])
                        
                cities = QgsVectorLayer("Point?crs=epsg:3857", point[1], "memory")
                if not cities.isValid(): raise Exception("Failed to create memory layer")
                pr = cities.dataProvider()
                cities.startEditing()
                #all points have the same columns
                pr.addAttributes([QgsField("admin_level", QVariant.String),QgsField("capital", QVariant.String),QgsField("name", QVariant.String),QgsField("place", QVariant.String),QgsField("population", QVariant.String)])

                selectedRows = []
                selectedFeatures = vlayer.getFeatures(request)
                for feature in selectedFeatures:
                    selectedRows.append(feature.id())
                    newFeature = QgsFeature()
                    newFeature.setGeometry(feature.geometry())
                    #all points have the same columns
                    newFeature.setAttributes([feature.attribute("admin_level"),feature.attribute("capital"),feature.attribute("name"),feature.attribute("place"),feature.attribute("population")])
                    pr.addFeatures([newFeature])

                cities.commitChanges()
                cities.updateExtents()
                vlayer.setSelectedFeatures(selectedRows)
                cities.setSelectedFeatures(selectedRows)
                mapLayer = QgsMapLayerRegistry.instance().addMapLayer(cities)

                #turn tables into tab files
                name = database + "/" + point[0]
                output = outputBase + name + ".tab"
                printCounts(mapLayer, name + ".tab")
                writeFile()
                getSize()

        elif table == "planet_osm_polygon":
            printCounts(vlayer, table)

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

                polys = QgsVectorLayer("Polygon?crs=epsg:3857", polygon[1], "memory")
                if not polys.isValid(): raise Exception("Failed to create memory layer")
                pr = polys.dataProvider()
                polys.startEditing()

                if polygon == states or polygon == counties:
                    pr.addAttributes([QgsField("admin_level",QVariant.String),QgsField("boundary",QVariant.String),QgsField("name",QVariant.String)])
                  
                    selectedRows = []
                    selectedFeatures = vlayer.getFeatures(request)
                    for feature in selectedFeatures:
                        selectedRows.append(feature.id())
                        newFeature = QgsFeature()
                        newFeature.setGeometry(feature.geometry())
                        newFeature.setAttributes([feature.attribute("admin_level"),feature.attribute("boundary"),feature.attribute("name")])
                        pr.addFeatures([newFeature])
                    polys.commitChanges()
                    polys.updateExtents()    
                    vlayer.setSelectedFeatures(selectedRows)
                    polys.setSelectedFeatures(selectedRows)
                    mapLayer = QgsMapLayerRegistry.instance().addMapLayer(polys)

                    #turn tables into tab files
                    name = database + "/" + polygon[0]
                    output = outputBase + name + ".tab"
                    printCounts(mapLayer, name + ".tab")
                    writeFile()

                elif polygon == urbanAreas:
                    pr.addAttributes([QgsField("admin_level",QVariant.String),QgsField("boundary",QVariant.String),QgsField("name",QVariant.String),QgsField("place",QVariant.String),QgsField("population",QVariant.String)])
                 
                    selectedRows = []
                    selectedFeatures = vlayer.getFeatures(request)
                    for feature in selectedFeatures:
                        selectedRows.append(feature.id())
                        newFeature = QgsFeature()
                        newFeature.setGeometry(feature.geometry())
                        newFeature.setAttributes([feature.attribute("admin_level"),feature.attribute("boundary"),feature.attribute("name"),feature.attribute("place"),feature.attribute("population")])
                        pr.addFeatures([newFeature])
                    polys.commitChanges()
                    polys.updateExtents()    
                    vlayer.setSelectedFeatures(selectedRows)
                    polys.setSelectedFeatures(selectedRows)
                    mapLayer = QgsMapLayerRegistry.instance().addMapLayer(polys)

                    #turn tables into tab files
                    name = database + "/" + polygon[0]
                    output = outputBase + name + ".tab"
                    printCounts(mapLayer, name + ".tab")
                    writeFile()
                    getSize()

                elif polygon == water:
                    pr.addAttributes([QgsField("landuse",QVariant.String),QgsField("natural",QVariant.String),QgsField("water",QVariant.String)])
                   
                    selectedRows = []
                    selectedFeatures = vlayer.getFeatures(request)
                    for feature in selectedFeatures:
                        selectedRows.append(feature.id())
                        newFeature = QgsFeature()
                        newFeature.setGeometry(feature.geometry())
                        newFeature.setAttributes([feature.attribute("landuse"),feature.attribute("natural"),feature.attribute("water")])
                        pr.addFeatures([newFeature])
                    polys.commitChanges()
                    polys.updateExtents()    
                    vlayer.setSelectedFeatures(selectedRows)
                    polys.setSelectedFeatures(selectedRows)
                    mapLayer = QgsMapLayerRegistry.instance().addMapLayer(polys)

                    #turn tables into tab files
                    name = database + "/" + polygon[0]
                    output = outputBase + name + ".tab"
                    printCounts(mapLayer, name + ".tab")
                    writeFile()
                    getSize()

                elif polygon == majorParks:
                    pr.addAttributes([QgsField("boundary",QVariant.String),QgsField("leisure",QVariant.String),QgsField("landuse",QVariant.String),QgsField("natural",QVariant.String),QgsField("water",QVariant.String),QgsField("place",QVariant.String)])
                   
                    selectedRows = []
                    selectedFeatures = vlayer.getFeatures(request)
                    for feature in selectedFeatures:
                        selectedRows.append(feature.id())
                        newFeature = QgsFeature()
                        newFeature.setGeometry(feature.geometry())
                        newFeature.setAttributes([feature.attribute("boundary"),feature.attribute("leisure"),feature.attribute("landuse"),feature.attribute("natural"),feature.attribute("water"),feature.attribute("place")])
                        pr.addFeatures([newFeature])
                    polys.commitChanges()
                    polys.updateExtents()    
                    vlayer.setSelectedFeatures(selectedRows)
                    polys.setSelectedFeatures(selectedRows)
                    mapLayer = QgsMapLayerRegistry.instance().addMapLayer(polys)

                    #turn tables into tab files
                    name = database + "/" + polygon[0]
                    output = outputBase + name + ".tab"
                    printCounts(mapLayer, name + ".tab")
                    writeFile()
                    getSize()

                elif polygon == landuse:
                    pr.addAttributes([QgsField("boundary",QVariant.String),QgsField("leisure",QVariant.String),QgsField("landuse",QVariant.String),QgsField("natural",QVariant.String),QgsField("water",QVariant.String),QgsField("place",QVariant.String),QgsField("military",QVariant.String)])
                 
                    selectedRows = []
                    selectedFeatures = vlayer.getFeatures(request)
                    for feature in selectedFeatures:
                        selectedRows.append(feature.id())
                        newFeature = QgsFeature()
                        newFeature.setGeometry(feature.geometry())
                        newFeature.setAttributes([feature.attribute("boundary"),feature.attribute("leisure"),feature.attribute("landuse"),feature.attribute("natural"),feature.attribute("water"),feature.attribute("place"),feature.attribute("military")])
                        pr.addFeatures([newFeature])
                    polys.commitChanges()
                    polys.updateExtents()    
                    vlayer.setSelectedFeatures(selectedRows)
                    polys.setSelectedFeatures(selectedRows)
                    mapLayer = QgsMapLayerRegistry.instance().addMapLayer(polys)

                    #turn tables into tab files
                    name = database + "/" + polygon[0]
                    output = outputBase + name + ".tab"
                    printCounts(mapLayer, name + ".tab")
                    writeFile()
                    getSize()

                elif polygon == airports:
                    pr.addAttributes([QgsField("boundary",QVariant.String),QgsField("leisure",QVariant.String),QgsField("landuse",QVariant.String),QgsField("natural",QVariant.String),QgsField("water",QVariant.String),QgsField("place",QVariant.String),QgsField("military",QVariant.String),QgsField("aeroway",QVariant.String)])
                
                    selectedRows = []
                    selectedFeatures = vlayer.getFeatures(request)
                    for feature in selectedFeatures:
                        selectedRows.append(feature.id())
                        newFeature = QgsFeature()
                        newFeature.setGeometry(feature.geometry())
                        newFeature.setAttributes([feature.attribute("boundary"),feature.attribute("leisure"),feature.attribute("landuse"),feature.attribute("natural"),feature.attribute("water"),feature.attribute("place"),feature.attribute("military"),feature.attribute("aeroway")])
                        pr.addFeatures([newFeature])
                    polys.commitChanges()
                    polys.updateExtents()    
                    vlayer.setSelectedFeatures(selectedRows)
                    polys.setSelectedFeatures(selectedRows)
                    mapLayer = QgsMapLayerRegistry.instance().addMapLayer(polys)

                    #turn tables into tab files
                    name = database + "/" + polygon[0]
                    output = outputBase + name + ".tab"
                    printCounts(mapLayer, name + ".tab")
                    writeFile()
                    getSize()

                else:
                    print "Not a valid polygon"

        elif table == "planet_osm_roads":
            printCounts(vlayer, table)

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

                road_mem = QgsVectorLayer("LineString?crs=epsg:3857", point[1], "memory")
                if not road_mem.isValid(): raise Exception("Failed to create memory layer")
                pr = road_mem.dataProvider()
                road_mem.startEditing()
                #all roads have the same columns
                pr.addAttributes([QgsField("name", QVariant.String),QgsField("highway", QVariant.String),QgsField("ref", QVariant.String),QgsField("surface", QVariant.String)])

                selectedRows = []
                selectedFeatures = vlayer.getFeatures(request)
                for feature in selectedFeatures:
                    selectedRows.append(feature.id())
                    newFeature = QgsFeature()
                    newFeature.setGeometry(feature.geometry())
                    #all roads have the same columns
                    newFeature.setAttributes([feature.attribute("name"),feature.attribute("highway"),feature.attribute("ref"),feature.attribute("surface")])
                    pr.addFeatures([newFeature])

                road_mem.commitChanges()
                road_mem.updateExtents()
                vlayer.setSelectedFeatures(selectedRows)
                road_mem.setSelectedFeatures(selectedRows)
                mapLayer = QgsMapLayerRegistry.instance().addMapLayer(road_mem)

                name = database + "/" + road[0]
                output = outputBase + name + ".tab"                
                printCounts(mapLayer, name + ".tab")
                writeFile()
                getSize()

        else:
            print "Bad table name."

message = "Process complete.\n\n\n"
logMessage()
logfile.close()
