#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 16/8/26 下午2:55
# Author  : youth
# Site    : www.imxingzhe.com
# File    : segment_macth.py
# Desc    :
import os
import ogr
import osr
import time
import math
import json
import gpxpy
import random
import gpxpy.gpx

from pyproj import Proj, transform

from shapely.geometry import Point, Polygon


"""
gdal is needed
pip install shapely gpxpy
"""

# distance to buffer polyline
BUFFER_DIS = 50


def get_gpx_data():
    alts = []

    with open('test.gpx', 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    alts.append(ll_to_proj((point.longitude + random.choice(xrange(1, 10)) / 1000,
                                            point.latitude + random.choice(xrange(1, 10)) / 1000)))

    return alts


def ll_to_proj(ll):
    p4326 = Proj(init='epsg:4326')
    p3857 = Proj(init='epsg:3857')

    return transform(p4326, p3857, ll[0], ll[1])


def proj_to_ll(proj):
    p4326 = Proj(init='epsg:4326')
    p3857 = Proj(init='epsg:3857')
    return transform(p3857, p4326, proj[0], proj[1])


def get_segment_from_gpx(filename):
    seg_line1 = 'LINESTRING ('
    seg_line2 = 'LINESTRING ('
    data = []
    with open(filename, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        for track in gpx.tracks:
            for segment in track.segments:
                for idx, point in enumerate(segment.points):
                    print point.longitude, point.latitude
                    data.append((
                        float(round(point.longitude, 6)) + random.choice(xrange(10, 100))/10000,
                        float(round(point.latitude, 6)) + random.choice(xrange(10, 100))/10000
                    ))
                    p = ll_to_proj((point.longitude, point.latitude))

                    if idx == 0:
                        seg_line1 += '%s %s' % (str(round(p[0], 3) + random.choice(xrange(10, 100))),
                                                str(round(p[1], 3) + random.choice(xrange(10, 100))))
                        seg_line2 += '%s %s' % (str(round(p[0], 3)),
                                                str(round(p[1], 3)))
                    else:
                        seg_line1 += ',%s %s' % (str(round(p[0], 3) + random.choice(xrange(10, 100))),
                                                 str(round(p[1], 3) + random.choice(xrange(10, 100))))
                        seg_line2 += ',%s %s' % (str(round(p[0], 3)),
                                                 str(round(p[1], 3)))

    return seg_line1 + ')', seg_line2 + ')', data


def export_geojson(geom, filename):
    outdriver = ogr.GetDriverByName('GeoJSON')

    # Create the output GeoJSON
    outdataSource = outdriver.CreateDataSource(filename)
    outlayer = outdataSource.CreateLayer(filename, geom_type=ogr.wkbPolygon)
    featureDefn = outlayer.GetLayerDefn()

    # create a new feature
    outfeature = ogr.Feature(featureDefn)

    # Set new geometry
    outfeature.SetGeometry(geom)

    outlayer.CreateFeature(outfeature)

    # destroy the feature
    outfeature.Destroy

    # Close DataSources
    outdataSource.Destroy()


def buffer_segment(segment):
    print 'create geometry'
    polyline = ogr.CreateGeometryFromWkt(segment[1])
    polyline1 = ogr.CreateGeometryFromWkt(segment[0])
    data = segment[2]

    print 'buffer'
    polyline_buffer = polyline.Buffer(BUFFER_DIS)
    print 'project'
    source_geom = osr.SpatialReference()
    source_geom.ImportFromEPSG(3857)

    target_geom = osr.SpatialReference()
    target_geom.ImportFromEPSG(4326)

    transform_geom = osr.CoordinateTransformation(source_geom, target_geom)

    polyline.Transform(transform_geom)
    polyline1.Transform(transform_geom)
    polyline_buffer.Transform(transform_geom)

    print 'remove js'
    try:
        os.remove('../geogo/polyline.geojson'),
        os.remove('../geogo/polyline1.geojson')
        os.remove('../geogo/polygon.geojson'),
    except:
        pass

    print 'export js'
    export_geojson(polyline, '../geogo/polyline.geojson')
    export_geojson(polyline1, '../geogo/polyline1.geojson')
    export_geojson(polyline_buffer, '../geogo/polygon.geojson')

    print 'judge within'

    start = time.time()
    # for i in range(0, polyline1.GetPointCount()):
    #     ll = polyline1.GetPoint(i)
    #     print ll
    for ll in data:
        p = ogr.CreateGeometryFromWkt('POINT (%s %s)' % (str(ll[0]), str(ll[1])))
        p.Within(polyline_buffer)
    end = time.time()
    print (end - start)

    # print len(get_gpx_data())
        #     p = ogr.CreateGeometryFromWkt('POINT (%s %s)' % (str(ll[0]), str(ll[1])))
        #
        #     print p.Within(polyline_buffer)

        # polyline.ExportToJson()


def run():
    line = get_segment_from_gpx('test.gpx')
    buffer_segment(line)

if __name__ == '__main__':
    import cProfile
    #
    # cProfile.run("run()")
    run()

