# Automate OSM Data Export from a PostGIS Database
Converts PostGIS tables into MapInfo Tab files.

## Overview

This script will automate and customize export of data from PostGIS databases into shapefiles.

PostGIS_To_Shp.py is a simple script that loops through all of the country databases and exports the data in "planet_osm_line", "planet_osm_point", "planet_osm_polygon", "planet_osm_roads" into shapefiles without customizeation. Warning: this may produce extremely large files.



These scripts were made for a specific project, and it is customized for that project. However, someone familiar with Python could easily modify queries and row/column names to suit their needs.

## Usage

You will need to have an existing set of PostGIS databases by country containing point, line, polygon, and road data from the OSM Planet file. You will also need QGIS Desktop. This was testing on version 2.8.1.

The script must be run in the QGIS Environment. To run, open the Python console in QGIS. Click the Editor button and then the Open button. Nagavate to the script and click Open. Now you can run the script within this console.


This script was origianlly intended to export MapInfo Tab files. However, the script that does the conversion outputs an early version of Tab file and does not get projected correctly.



