from django.shortcuts import render, get_object_or_404

from sources.models import Source


def source_index(request):

    context = {
        'sources': Source.objects.order_by('-total', 'name')
        }
    return render(request, 
                  "sources/index.html",
                  context)


def source_detail(request, source_id):
    source = get_object_or_404(Source, id=source_id)
    context = {
        'source': source,
        #'feeds': source.feeditem_set.order_by('-dt'),
        }
    return render(request, 
                  "sources/detail.html",
                  context)






