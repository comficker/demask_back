from django.http import HttpResponse
from django.template import loader
from app.models import Contract
from datetime import datetime


def sitemap_style(request):
    template = loader.get_template('./main-sitemap.xsl')
    return HttpResponse(template.render({}, request), content_type='text/xml')


def sitemap_index(request):
    sm = [
        "https://demask.io/collection-sitemap.xml",
    ]
    template = loader.get_template('./sitemap_index.xml')
    return HttpResponse(template.render({
        "sitemaps": sm
    }, request), content_type='text/xml')


def sitemap_detail(request, flag):
    template = loader.get_template('./sitemap.xml')
    if flag == "collection":
        ds = list(map(
            lambda x: {
                "location": "https://demask.io/collection/{}".format(x.address),
                "priority": 0.8,
                "updated": datetime.now(),
                "changefreq": "daily"
            },
            Contract.objects.all()
        ))
    else:
        ds = []
    return HttpResponse(template.render({
        "dataset": ds
    }, request), content_type='text/xml')
