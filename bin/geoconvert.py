#!/bin/python
#-*- coding: utf-8 -*-
import splunk.Intersplunk, splunk.util
import itertools
import GeoConverter

def geoconvert(results, settings):

    try:
        fields, argvals = splunk.Intersplunk.getKeywordsAndOptions()
        for r in results:
            if len(fields)>1:
                pt = GeoConverter.GeoPoint(float(r['x']), float(r['y']))
                output = GeoConverter.convert(GeoConverter.KATEC, GeoConverter.GEO, pt)
                r['x_long'] = output.getX()
                r['y_lat'] = output.getY() 
        splunk.Intersplunk.outputResults(results)
    except:
        import traceback
        stack =  traceback.format_exc()
        results = splunk.Intersplunk.generateErrorResults("Error : Traceback: " + str(stack))

results, dummyresults, settings = splunk.Intersplunk.getOrganizedResults()
geoconvert(results, settings)

