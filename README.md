## Overview

This script will automate and customize export of data from PostGIS databases into shapefiles.

[Export_All.py] (https://github.com/christyheaton/PostGIS_Tab_Convert/blob/master/Export_All.py) is a simple script that loops through all of the country databases and exports the data in "planet_osm_line", "planet_osm_point", "planet_osm_polygon", "planet_osm_roads" into shapefiles without customization. Warning: this may produce extremely large files.

[Export_Custom.py] (https://github.com/christyheaton/PostGIS_Tab_Convert/blob/master/Export_Custom.py) is more complex. It allows for a subset of rows and columns to be exported to the final shapefiles, saving a space and producing an output that only contains the data you need. In testing this produced much smaller and more workable files than Export_All.py.

## Usage

### Preconditions

1. You will need to have an existing set of PostGIS databases by country containing point, line, polygon, and road data from the OSM Planet file. The script will need to be modified to point to your server, with its own username and password.
```python
server = "MyServer"
uri.setConnection(server, "5432", database, "username", "password")
```

2. You will need [QGIS Desktop] (https://www.qgis.org/en/site/forusers/download.html) (this was tested using version 2.8.1).

3. You will need to set up output folders in your output directory. You can use the MakeFolders.bat file to create your folders. Just put it in your output directory and double click the file to run.

### Customize

To customize rows, you must decide on a name for your output and a query QGIS can use to select it. For example, the point table contains all points in the planet file and I want to produce separate shapefiles representing Cities, Suburbs. Towns, etc. This can be customized for other needs.

```python
        if table == "planet_osm_point":
            printCounts(vlayer, table)

            cities1 = ["Cities_City", r"""place = 'city'"""]
            cities2 = ["Cities_Suburb", r"""place = 'suburb'"""]
            cities3 = ["Cities_Town", r"""place = 'town'"""]
            cities4 = ["Cities_Village", r"""place = 'village'"""]
            cities6 = ["Cities_Neighborhood", r"""place = 'neighborhood'"""]
            cities8 = ["Cities_Locality", r"""place in ('locality','hamlet')"""]
            stateLabels = ["StateLabels", r"""place in ('state','province')"""]
```

To customize columns, the script creates a memory layer and builds just the columns explicitly requested. Then it populates them with the columns with the same name from the original table. Both these lines of code must contain the same custom columns.

```python
pr.addAttributes([QgsField("osm_id", QVariant.Int),QgsField("admin_level", QVariant.String),QgsField("capital", QVariant.String),QgsField("name", QVariant.String),QgsField("place", QVariant.String),QgsField("population", QVariant.Int),QgsField("tags", QVariant.String)])

newFeature.setAttributes([feature.attribute("osm_id"),feature.attribute("admin_level"),feature.attribute("capital"),feature.attribute("name"),feature.attribute("place"),feature.attribute("population"), feature.attribute("tags")])
```

### Running the script

The script must be run in the QGIS Environment. To run, open the Python console in QGIS. Click the Editor button and then the Open button. Nagavate to the script and click Open. Now you can run the script within this console.

## Limitations

This script was origianlly intended to export MapInfo Tab files. However, the script that does the conversion outputs an early version of Tab file and does not get projected correctly. Now the conversion it to Esri Shapefile and later converted to Mapinfo Tab using a modern conversion tool.



