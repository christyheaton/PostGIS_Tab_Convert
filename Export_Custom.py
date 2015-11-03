'''
This script automates and customizes the export of OSM planet data in PostGIS databases into shp files.
It must be run in the QGIS environment. Tested in QGIS 2.8.1.
You need to have existing folders in your output directory with the same names as in the database list.
You must also have a server containing PostGIS databases (by country) with point, line, polygon, and road tables. 
'''
import os
from time import strftime
from PyQt4.QtCore import QVariant
# define output directory
outputBase = r"C:/Temp/"
if not os.path.exists(outputBase):
    print "Invalid directory"
logfile = open(outputBase + "logfile.txt", "a+")

def logMessage():
    '''Prints a message to the QGIS python window and logs in a file.'''
    print strftime("%Y-%m-%d %H:%M:%S") + " " + message
    logfile.write(strftime("%Y-%m-%d %H:%M:%S") + " " + message)

def printCounts(layer, name):
    '''Finds the row and column counts of the current table and prints and logs the counts.'''
    fields = layer.pendingFields()
    num_fields = len(fields)
    num_rows = layer.featureCount()
    message = name + ' has ' + str(num_rows) + ' rows and ' + str(num_fields) + ' columns.\n'
    print strftime("%Y-%m-%d %H:%M:%S") + " " + message
    logfile.write(strftime("%Y-%m-%d %H:%M:%S") + " " + message)

def writeFile():
    '''Writes the memory layer to a Shapefile and prints and logs a completion message when done.'''
    QgsVectorFileWriter.writeAsVectorFormat(mapLayer, output, encoding, coordsys, "ESRI Shapefile")
    message = "Translation of " + name + ".shp successful.\n"
    print strftime("%Y-%m-%d %H:%M:%S") + " " + message
    logfile.write(strftime("%Y-%m-%d %H:%M:%S") + " " + message)

def getSize():
    '''Gets the size of the data file and prints and logs this info.'''
    dataFile = outputBase + name + ".dbf"
    sizeK = float(os.path.getsize(dataFile))/1024
    message = name + ".dbf" + " size: " + str("%.2f" % sizeK) + " KB.\n"
    print strftime("%Y-%m-%d %H:%M:%S") + " " + message
    logfile.write(strftime("%Y-%m-%d %H:%M:%S") + " " + message)

message = "PostGIS_Tab_Convert.py started...\n"
logMessage()

message = "Output will go in individual country folders in " + outputBase + "\n"
logMessage()

# create databases list. To run just El Salvador, for example, change to ["SV"]
databases = ["AQ", "AR", "BR", "CA", "CL", "CR", "CU", "DE", "ES", "GB", "GT", "JP", "KR", "MX", "NG", "NI", "PA", "RU", "SV"]

message = "Databases:" + str(databases) + "\n"
logMessage()

# create list of table names - this is the same for all databases
tableList = ["planet_osm_line", "planet_osm_point", "planet_osm_polygon"]

message = "Table list:" + str(tableList) + "\n"
logMessage()

# set up server, encoding, and coordinate system
server = "MyServer"
encoding = "utf-8"
coordsys = QgsCoordinateReferenceSystem(3395, QgsCoordinateReferenceSystem.EpsgCrsId)

# connect to server
uri = QgsDataSourceURI()

for database in databases:
    # connect to current database
    uri.setConnection(server, "5432", database, "username", "password")
    
    message = "Connection to " + server + " " + database + " established.\n"
    logMessage()

    # go through every table in the list and turn it into a QGISVectorLayer
    for table in tableList:
        message = "Connection to " + database + ": " + table + " established.\n"
        logMessage()
        uri.setDataSource("public", table, "way")
        vlayer = QgsVectorLayer(uri.uri(), table, "postgres")

        if table == "planet_osm_line":
            printCounts(vlayer, table)

            # change this to customize your selection [name, query]
            railway = ["Railway", r""""railway" != ''"""]
            expressway = ["Expressways", r""""highway" like '%motorway%' or  "highway" like '%trunk%'"""]
            primaryHighway = ["PrimaryHighway", r""""highway" = 'primary'"""]
            secondaryHighway = ["SecondaryHighway", r""""highway" = 'secondary'"""]
            regionalHighway = ["RegionalHighway", r""""highway" = 'tertiary'"""]
            localRoutes = ["LocalRoutes", r""""highway" = 'unclassified'"""]
            streets = ["Streets", r""""highway" like '%residential%' or "highway" like '%service%' or "highway" like '%living_street%'"""]

            lines = [railway, expressway, primaryHighway, secondaryHighway, regionalHighway, localRoutes, streets]

            for line in lines:
                
                request = QgsFeatureRequest()
                request.setFilterExpression(line[1])

                line_mem = QgsVectorLayer("LineString?crs=epsg:3857", "lines", "memory")
                if not line_mem.isValid(): raise Exception("Failed to create memory layer")
                pr = line_mem.dataProvider()
                line_mem.startEditing()
                pr.addAttributes([QgsField("osm_id", QVariant.String),QgsField("name", QVariant.String),QgsField("highway", QVariant.String),QgsField("ref", QVariant.String),QgsField("surface", QVariant.String),QgsField("railway", QVariant.String)])
    
                selectedRows = []
                selectedFeatures = vlayer.getFeatures(request)
    
                for feature in selectedFeatures:
                    selectedRows.append(feature.id())
                    newFeature = QgsFeature()
                    newFeature.setGeometry(feature.geometry())
                    newFeature.setAttributes([feature.attribute("osm_id"),feature.attribute("name"),feature.attribute("highway"),feature.attribute("ref"),feature.attribute("surface"),feature.attribute("railway")])
                    pr.addFeatures([newFeature])
    
                line_mem.commitChanges()
                line_mem.updateExtents()
                vlayer.setSelectedFeatures(selectedRows)
                line_mem.setSelectedFeatures(selectedRows)
                mapLayer = QgsMapLayerRegistry.instance().addMapLayer(line_mem)

                #turn tables into tab files
                name = database + "/" + line[0]
                output = outputBase + name + ".shp"
                printCounts(mapLayer, name + ".shp")
                writeFile()
                getSize()

        elif table == "planet_osm_point":
            printCounts(vlayer, table)

            # change this to customize your selection [name, query]
            city = ["Cities_City", r"""place = 'city'"""]
            suburb = ["Cities_Suburb", r"""place = 'suburb'"""]
            town = ["Cities_Town", r"""place = 'town'"""]
            village = ["Cities_Village", r"""place = 'village'"""]
            neighborhood = ["Cities_Neighborhood", r"""place = 'neighborhood'"""]
            locality = ["Cities_Locality", r"""place in ('locality','hamlet')"""]
            stateLabels = ["StateLabels", r"""place in ('state','province')"""]
            
            points = [city, suburb, town, village, neighborhood, locality, stateLabels]

            for point in points:
                request = QgsFeatureRequest()
                request.setFilterExpression(point[1])
                # create a point memory layer using epsg 3857, select just rows that fit the query in point[1]        
                cities = QgsVectorLayer("Point?crs=epsg:3857", point[1], "memory")
                if not cities.isValid(): raise Exception("Failed to create memory layer")
                pr = cities.dataProvider()
                cities.startEditing()
                # create columns in the memory layer, all point tables will have the same columns (no interior loop needed)
                pr.addAttributes([QgsField("osm_id", QVariant.String),QgsField("name", QVariant.String),QgsField("admin_level", QVariant.String),QgsField("capital", QVariant.String),QgsField("name", QVariant.String),QgsField("place", QVariant.String),QgsField("population", QVariant.String)])

                selectedRows = []
                selectedFeatures = vlayer.getFeatures(request)
                for feature in selectedFeatures:
                    selectedRows.append(feature.id())
                    newFeature = QgsFeature()
                    newFeature.setGeometry(feature.geometry())
                    # populate the memory layer with matching fields from from the table
                    newFeature.setAttributes([feature.attribute("osm_id"),feature.attribute("name"),feature.attribute("admin_level"),feature.attribute("capital"),feature.attribute("name"),feature.attribute("place"),feature.attribute("population")])
                    pr.addFeatures([newFeature])

                cities.commitChanges()
                cities.updateExtents()
                vlayer.setSelectedFeatures(selectedRows)
                cities.setSelectedFeatures(selectedRows)
                mapLayer = QgsMapLayerRegistry.instance().addMapLayer(cities)

                # turn tables into shapefiles
                name = database + "/" + point[0]
                output = outputBase + name + ".shp"
                printCounts(mapLayer, name + ".shp")
                writeFile()
                getSize()

        elif table == "planet_osm_polygon":
            printCounts(vlayer, table)

            # change this to customize your selection [name, query]
            states = ["States", r"""("boundary" != '' and "admin_level"='4') or ("place" like '%state%' or "place" like '%province%')"""]
            counties = ["Counties", r""""boundary" <> '' and ("admin_level" = '6' or "place" = 'county')"""]
            urbanAreas = ["UrbanAreas", r"""("boundary" != '' and ("admin_level"='7' or "admin_level" = '8')) or ("place" like '%city%' or "place" like '%municipality%')"""]
            water = ["Water", r"""water is not null or waterway = 'riverbank' or waterway = 'channel' or waterway = 'fishing_lake' or waterway = 'lake' or waterway = 'moat' or waterway = 'mill_pond' or waterway = 'pond' or waterway = 'reservoir' or waterway = 'river' or waterway = 'stream' or waterway = 'water' or waterway = 'waterfall' or waterway = 'yes' or 'waterway' = 'weir' or waterway = 'marina' or waterway = 'mooring' or "natural" like '%bay%' or  "natural" like '%water%' or  "landuse" = 'reservoir'"""]
            majorParks = ["MajorParks", r""""boundary" in ('national_park')"""]
            landuse = ["Landuse", r""""landuse" in ('forest','recreation_ground','railway','military') or "boundary" = 'protected_area' or "military" <> '' or "railway" = 'station' or "leisure" = 'park'"""]
            airports = ["Airports", r""""aeroway"<>''"""]

            polygons = [states, counties, urbanAreas, water, majorParks, landuse, airports]

            for polygon in polygons:
                request = QgsFeatureRequest()
                request.setFilterExpression(polygon[1])

                # create a polygon memory layer using epsg 3857, select just rows that fit the query in polygon[1]
                polys = QgsVectorLayer("Polygon?crs=epsg:3857", polygon[1], "memory")
                if not polys.isValid(): raise Exception("Failed to create memory layer")
                pr = polys.dataProvider()
                polys.startEditing()

                # polygon table contains a variety of themes and more customization of columns
                if polygon == states or polygon == counties:
                    # create columns in the memory layer, states and counties will have the same columns
                    pr.addAttributes([QgsField("osm_id",QVariant.String),QgsField("name", QVariant.String),QgsField("admin_level",QVariant.String),QgsField("boundary",QVariant.String),QgsField("name",QVariant.String)])
                  
                    selectedRows = []
                    selectedFeatures = vlayer.getFeatures(request)
                    for feature in selectedFeatures:
                        selectedRows.append(feature.id())
                        newFeature = QgsFeature()
                        newFeature.setGeometry(feature.geometry())
                        # populate the memory layer with matching fields from from the table
                        newFeature.setAttributes([feature.attribute("osm_id"),feature.attribute("name"),feature.attribute("admin_level"),feature.attribute("boundary"),feature.attribute("name")])
                        pr.addFeatures([newFeature])
                    polys.commitChanges()
                    polys.updateExtents()    
                    vlayer.setSelectedFeatures(selectedRows)
                    polys.setSelectedFeatures(selectedRows)
                    mapLayer = QgsMapLayerRegistry.instance().addMapLayer(polys)

                    #turn tables into shapefiles
                    name = database + "/" + polygon[0]
                    output = outputBase + name + ".shp"
                    printCounts(mapLayer, name + ".shp")
                    writeFile()

                elif polygon == urbanAreas:
                    # create columns in the memory layer
                    pr.addAttributes([QgsField("osm_id",QVariant.String),QgsField("name", QVariant.String),QgsField("admin_level",QVariant.String),QgsField("boundary",QVariant.String),QgsField("name",QVariant.String),QgsField("place",QVariant.String),QgsField("population",QVariant.String)])
                 
                    selectedRows = []
                    selectedFeatures = vlayer.getFeatures(request)
                    for feature in selectedFeatures:
                        selectedRows.append(feature.id())
                        newFeature = QgsFeature()
                        newFeature.setGeometry(feature.geometry())
                        # populate the memory layer with matching fields from from the table
                        newFeature.setAttributes([feature.attribute("osm_id"),feature.attribute("name"),feature.attribute("admin_level"),feature.attribute("boundary"),feature.attribute("name"),feature.attribute("place"),feature.attribute("population")])
                        pr.addFeatures([newFeature])
                    polys.commitChanges()
                    polys.updateExtents()    
                    vlayer.setSelectedFeatures(selectedRows)
                    polys.setSelectedFeatures(selectedRows)
                    mapLayer = QgsMapLayerRegistry.instance().addMapLayer(polys)

                    #turn tables into shapefiles
                    name = database + "/" + polygon[0]
                    output = outputBase + name + ".shp"
                    printCounts(mapLayer, name + ".shp")
                    writeFile()
                    getSize()

                elif polygon == water:
                    # create columns in the memory layer
                    pr.addAttributes([QgsField("osm_id",QVariant.String),QgsField("name", QVariant.String),QgsField("landuse",QVariant.String),QgsField("natural",QVariant.String),QgsField("water",QVariant.String)])
                   
                    selectedRows = []
                    selectedFeatures = vlayer.getFeatures(request)
                    for feature in selectedFeatures:
                        selectedRows.append(feature.id())
                        newFeature = QgsFeature()
                        newFeature.setGeometry(feature.geometry())
                        # populate the memory layer with matching fields from from the table
                        newFeature.setAttributes([feature.attribute("osm_id"),feature.attribute("name"),feature.attribute("landuse"),feature.attribute("natural"),feature.attribute("water")])
                        pr.addFeatures([newFeature])
                    polys.commitChanges()
                    polys.updateExtents()    
                    vlayer.setSelectedFeatures(selectedRows)
                    polys.setSelectedFeatures(selectedRows)
                    mapLayer = QgsMapLayerRegistry.instance().addMapLayer(polys)

                    #turn tables into shapefiles
                    name = database + "/" + polygon[0]
                    output = outputBase + name + ".shp"
                    printCounts(mapLayer, name + ".shp")
                    writeFile()
                    getSize()

                elif polygon == majorParks:
                    # create columns in the memory layer
                    pr.addAttributes([QgsField("osm_id",QVariant.String),QgsField("name", QVariant.String),QgsField("boundary",QVariant.String),QgsField("leisure",QVariant.String),QgsField("landuse",QVariant.String),QgsField("natural",QVariant.String),QgsField("water",QVariant.String),QgsField("place",QVariant.String)])
                   
                    selectedRows = []
                    selectedFeatures = vlayer.getFeatures(request)
                    for feature in selectedFeatures:
                        selectedRows.append(feature.id())
                        newFeature = QgsFeature()
                        newFeature.setGeometry(feature.geometry())
                        # populate the memory layer with matching fields from from the table
                        newFeature.setAttributes([feature.attribute("osm_id"),feature.attribute("name"),feature.attribute("boundary"),feature.attribute("leisure"),feature.attribute("landuse"),feature.attribute("natural"),feature.attribute("water"),feature.attribute("place")])
                        pr.addFeatures([newFeature])
                    polys.commitChanges()
                    polys.updateExtents()    
                    vlayer.setSelectedFeatures(selectedRows)
                    polys.setSelectedFeatures(selectedRows)
                    mapLayer = QgsMapLayerRegistry.instance().addMapLayer(polys)

                    #turn tables into shapefiles
                    name = database + "/" + polygon[0]
                    output = outputBase + name + ".shp"
                    printCounts(mapLayer, name + ".shp")
                    writeFile()
                    getSize()

                elif polygon == landuse:
                    # create columns in the memory layer
                    pr.addAttributes([QgsField("osm_id",QVariant.String),QgsField("name", QVariant.String),QgsField("boundary",QVariant.String),QgsField("leisure",QVariant.String),QgsField("landuse",QVariant.String),QgsField("natural",QVariant.String),QgsField("water",QVariant.String),QgsField("place",QVariant.String),QgsField("military",QVariant.String)])
                 
                    selectedRows = []
                    selectedFeatures = vlayer.getFeatures(request)
                    for feature in selectedFeatures:
                        selectedRows.append(feature.id())
                        newFeature = QgsFeature()
                        newFeature.setGeometry(feature.geometry())
                        # populate the memory layer with matching fields from from the table
                        newFeature.setAttributes([feature.attribute("osm_id"),feature.attribute("name"),feature.attribute("boundary"),feature.attribute("leisure"),feature.attribute("landuse"),feature.attribute("natural"),feature.attribute("water"),feature.attribute("place"),feature.attribute("military")])
                        pr.addFeatures([newFeature])
                    polys.commitChanges()
                    polys.updateExtents()    
                    vlayer.setSelectedFeatures(selectedRows)
                    polys.setSelectedFeatures(selectedRows)
                    mapLayer = QgsMapLayerRegistry.instance().addMapLayer(polys)

                    #turn tables into shapefiles
                    name = database + "/" + polygon[0]
                    output = outputBase + name + ".shp"
                    printCounts(mapLayer, name + ".shp")
                    writeFile()
                    getSize()

                elif polygon == airports:
                    # create columns in the memory layer
                    pr.addAttributes([QgsField("osm_id",QVariant.String),QgsField("name", QVariant.String),QgsField("boundary",QVariant.String),QgsField("leisure",QVariant.String),QgsField("landuse",QVariant.String),QgsField("natural",QVariant.String),QgsField("water",QVariant.String),QgsField("place",QVariant.String),QgsField("military",QVariant.String),QgsField("aeroway",QVariant.String)])
                    selectedRows = []
                    selectedFeatures = vlayer.getFeatures(request)
                    for feature in selectedFeatures:
                        selectedRows.append(feature.id())
                        newFeature = QgsFeature()
                        newFeature.setGeometry(feature.geometry())
                        # populate the memory layer with matching fields from from the table
                        newFeature.setAttributes([feature.attribute("osm_id"),feature.attribute("name"),feature.attribute("boundary"),feature.attribute("leisure"),feature.attribute("landuse"),feature.attribute("natural"),feature.attribute("water"),feature.attribute("place"),feature.attribute("military"),feature.attribute("aeroway")])
                        pr.addFeatures([newFeature])
                    polys.commitChanges()
                    polys.updateExtents()    
                    vlayer.setSelectedFeatures(selectedRows)
                    polys.setSelectedFeatures(selectedRows)
                    mapLayer = QgsMapLayerRegistry.instance().addMapLayer(polys)

                    #turn tables into shapefiles
                    name = database + "/" + polygon[0]
                    output = outputBase + name + ".shp"
                    printCounts(mapLayer, name + ".shp")
                    writeFile()
                    getSize()

                else:
                    print "Not a valid polygon"
        else:
            print "Bad table name."

message = "Process complete.\n\n\n"
logMessage()
logfile.close()
