from django.shortcuts import render, redirect
from userAuth.decorators import login_required_custom
from .models import Portfolio
from django.db.models import Max, F
from .utils import FetchPortfolio, CalculatePnL

# Create your views here.
@login_required_custom
def index(request):
    
    view_request(request)
    userId = request.myuser.userId
    #print("User ID:", userId)
    

    pfHelper = (
        Portfolio.objects.filter(user_id=userId)
        .values('stock')
        .annotate(maxDate = Max('transactionDate'))
    )

    pf = (
        Portfolio.objects.filter(
            transactionDate__in = [x['maxDate'] for x in pfHelper]
        ).select_related('stock')
        .annotate(currentValue = F('stock__price') * F('runningQtyAfter'))
        .annotate(investmentCost = F('transactionPrice') * F('runningQtyAfter'))
        .annotate(unrealizedProfit = F('currentValue') - F('investmentCost'))
    )

    print(pf)

    txns = FetchPortfolio(userId)
    txns = CalculatePnL(txns)

    for stock in pf:
        stock.realizedProfit = txns.get(stock.stock.stockName)

    print(txns)
    
    context = {
        'portfolio' : pf,
        'transactions' : txns,
    }
    return render(request, 'portfolio/index.html', context)

def view_request(request):
    print("Method:", request.method)
    print("GET params:", request.GET)
    print("POST data:", request.POST)
    print("Uploaded files:", request.FILES)
    print("Path:", request.path)
    print("Full path:", request.get_full_path())
    print("User agent:", request.META.get('HTTP_USER_AGENT'))
    print("Client IP:", request.META.get('REMOTE_ADDR'))
    print("Cookies:", request.COOKIES)
    print("Session:", request.session)
    print("Logged-in user:", request.user)
