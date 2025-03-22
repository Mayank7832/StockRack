from django.shortcuts import render
from .models import Portfolio
from django.db.models import Max
from .utils import FetchPortfolio, CalculatePnL

# Create your views here.
def index(request):
    view_request(request)

    pfHelper = (
        Portfolio.objects.filter(user_id=2)
        .values('stock')
        .annotate(maxDate = Max('transactionDate'))
    )

    pf = (
        Portfolio.objects.filter(
            transactionDate__in = [x['maxDate'] for x in pfHelper]
        ).select_related('stock')
    )

    print(pf)

    txns = FetchPortfolio(2)
    txns = CalculatePnL(txns)

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
