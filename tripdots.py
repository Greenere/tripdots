#coding=utf-8
import json
import os
import sys
import exifread

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

def getLocation(fp):
    exif_dict=exifread.process_file(fp)

    #get longitude
    lon_ref = exif_dict["GPS GPSLongitudeRef"].printable
    lon = exif_dict["GPS GPSLongitude"].printable[1:-1].replace(" ", "").replace("/", ",").split(",")
    lon = float(lon[0]) + float(lon[1]) / 60 + float(lon[2]) / float(lon[3]) / 3600
    if lon_ref != "E":
        lon = lon * (-1)

    #get lattitude
    lat_ref = exif_dict["GPS GPSLatitudeRef"].printable
    lat = exif_dict["GPS GPSLatitude"].printable[1:-1].replace(" ", "").replace("/", ",").split(",")
    lat = float(lat[0]) + float(lat[1]) / 60 + float(lat[2]) / float(lat[3]) / 3600
    if lat_ref != "N":
        lat = lat * (-1)

    #get time
    dateTime=str(exif_dict['Image DateTime'])
    dt=dateTime.split(' ')[0]

    return (lat,lon),dt

def makeLocationList(path, fileName='locationDict.json'):
    files = os.listdir(path)
    locations = {}
    latitudes = []
    longitudes = []
    failures=0
    success=0
    for file in files:
        try:
            with open(path+'/'+file,'rb') as f:
                location,dt=getLocation(f)
                success+=1
            try:
                locations[dt].append(location)
            except:
                locations[dt] = [location]
            latitudes.append(location[0])
            longitudes.append(location[1])
        except:
            failures+=1

    locationDict={
        'locations':locations,
        'lats':latitudes,
        'lons':longitudes
    }

    json.dump(locationDict,open(fileName,'w'), indent=2)

    print("Location dict is saved to %s, success: %d, failures: %d "
          % (fileName, success, failures))

    return locationDict

def pinLocations(fileName, shapefiles = 'gadm36_CHN_shp/gadm36_CHN_2',
                 withlegend = False):
    with open(fileName,'r') as f:
        locationDict=json.load(f)

    lats=locationDict['lats']
    lons=locationDict['lons']

    if len(lats) < 1:
        print("No location information")
        return

    locations=locationDict['locations']

    minlat=min(lats) - 0.1 * (max(lats) - min(lats))
    maxlat=max(lats) + 0.1 * (max(lats) - min(lats))
    minlon=min(lons) - 0.1 * (max(lons) - min(lons))
    maxlon=max(lons) + 0.1 * (max(lons) - min(lons))

    plt.figure()
    ax=plt.gca()

    map=Basemap(projection='mill',
                llcrnrlat=minlat,
                llcrnrlon=minlon,
                urcrnrlat=maxlat,
                urcrnrlon=maxlon,
                resolution='h')

    map.readshapefile(shapefiles, 'states',
                      drawbounds=True, linewidth=0.2)
    #map.drawcoastlines()

    for key in locations.keys():
        if len(locations[key]) == 0:
            continue
        lats=[]
        lons=[]
        for loc in locations[key]:
            lats.append(loc[0])
            lons.append(loc[1])
        x,y=map(lons,lats)
        map.scatter(x,y,s=1,
                    alpha=0.5, zorder=1, label=key.replace(':','-'))

    ax.set_xlabel('Trip Dots')

    if withlegend:
        plt.legend(title='Date')

    plt.show()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        print("Please designate a path containing images to process")
        path = None
        quit(1)
    #path = 'D:/works/照片/云南/pictures'
    fileName = 'locationDict.json'
    makeLocationList(path, fileName)
    pinLocations(fileName)
