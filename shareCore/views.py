# Create your views here.

import math
import sys

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils.safestring import mark_safe
from django.template import RequestContext
from django.utils import simplejson
from django.conf import settings

from share2.shareCore.Pager import Pager

class ViewCore:
    def getMatchingFeatures(self, request):
        query = request.REQUEST.get('q', '')
        return self.getMatchingFeaturesForQuery(query)

    def getGalleryData(self, request, page):
        pager = Pager(baseUrl=request.build_absolute_uri('..').rstrip('/'),
                      items=self.getMatchingFeatures(request),
                      pageSize=settings.GALLERY_PAGE_ROWS*settings.GALLERY_PAGE_COLS,
                      pageNum=int(page))
        pageData = pager.slice()
        for i, item in enumerate(pageData):
            item.row = i // settings.GALLERY_PAGE_COLS
        return pager, pageData

    def gallery(self, request, page):
        pager, pageData = self.getGalleryData(request, page)
        return render_to_response('gallery.html',
                                  dict(pager = pager,
                                       data = pageData),
                                  context_instance=RequestContext(request))
    
    def getGalleryJsonText(self, request):
        features = [f.asLeafClass() for f in self.getMatchingFeatures(request)]
        return simplejson.dumps([f.getShortDict() for f in features],
                                separators=(',',':') # omit spaces
                                )

    def galleryJson(self, request):
        return HttpResponse(self.getGalleryJsonText(request), mimetype='application/json')

    def galleryJsonJs(self, request):
        return render_to_response('galleryJson.js',
                                  dict(galleryJsonText = self.getGalleryJsonText(request)),
                                  mimetype='application/json')

    def main(self, request):
        pager, pageData = self.getGalleryData(request, '1')
        return render_to_response('main.html',
                                  dict(pager = pager,
                                       data = pageData),
                                  context_instance=RequestContext(request))

    def kml(request):
        kml = self.getKml(request)
        return HttpResponse(kml, mimetype='application/vnd.google-earth.kml+xml')
