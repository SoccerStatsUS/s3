from collections import defaultdict, OrderedDict, Counter

from django.shortcuts import render

from django.shortcuts import render, get_object_or_404
# Create your views here.

from .models import Transaction

from teams.models import Team

#@cache_page(60 * 60 * 12)
def transaction_index(request):
    """
    Teams shown by letter.
    """
    # This is not good but not sure how to fix.
    # Need to broaden team standing generation so we use that
    # to pull all teams.
    
    letters = 'abcdefghijklmnopqrstuvwxyz'.upper()

    #name_dict = OrderedDict()

    #standings = Standing.objects.filter(competition=None)

    """
    for letter in letters:
        #teams = Team.objects.filter(name__istartswith=letter)
        #team_standings = standings.filter(team__name__istartswith=letter)[:10]
        #name_dict[letter] = team_standings
        #name_dict[letter] = teams
        pass
    """
        
    #context = {
    #    'name_dict': name_dict,
    #    }

    transactions = Transaction.objects.order_by('-date').select_related()

    context = {
        'transactions': transactions,
        }

    return render(request, 
                  "transactions/index.html",
                  context)




def transaction_detail(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    context = {
        'transaction': transaction, 
        }
    return render(request, 
                              "transactions/detail.html",
                              context)
