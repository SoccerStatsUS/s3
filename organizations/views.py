from django.shortcuts import render, get_object_or_404



from organizations.models import Confederation


def organizations_index(request):

    context = {
        'confederations': Confederation.objects.all(),
        }
    

    return render(request,
        "organizations/index.html",
        context)




#@cache_page(60 * 60 * 12)
def confederations_index(request):

    context = {
        'confederations': Confederation.objects.all(),
        }
    

    return render(request,
                  "organizations/confederation/index.html",
                  context)




#@cache_page(60 * 60 * 12)
def confederation_detail(request, confederation_slug):
    confederation = get_object_or_404(Confederation, slug=confederation_slug)

    context = {
        'confederation': confederation,
        }

    return render(request,
                  "organizations/confederation/detail.html",
                  context)
