from django.shortcuts import render, redirect
from django.contrib import messages
from userAuth.decorators import login_required_custom
from django.views.decorators.http import require_POST
from .models import Portfolio
=======
from .forms import TradeForm
from .models import Trade
>>>>>>> f030fc59f63ca5d2d26471b3ca998620bbad7757
from .utils import PortfolioService

# Create your views here.
@login_required_custom
def index(request):
    
    view_request(request)
    user = request.myuser
    portfolio = PortfolioService(user).fetch_portfolio()

    context = {
        'portfolio' : portfolio,
    }
    return render(request, 'portfolio/index.html', context)

def delete_stock(request, stockId):
    """
    Delete a stock from the portfolio.
    """
    if request.method == "POST":
        txns = Trade.objects.filter(stock_id=stockId, user=request.myuser.userId)
        txns.delete()
        messages.success(request, "Stock deleted successfully!")
    return redirect('portfolio:index')

def add_trade(request):
    if request.method == 'POST':
        form = TradeForm(request.POST)
        if form.is_valid():
            stock = form.cleaned_data['stock']
            stockQty = form.cleaned_data['quantity']
            transactionPrice = form.cleaned_data['trade_price']
            transactionType = form.cleaned_data['direction']
            transactionDate = form.cleaned_data['date']

            portfolio = Trade(
                user=request.myuser,
                stock=stock,
                quantity=stockQty,
                trade_price=transactionPrice,
                direction=transactionType,
                date=transactionDate,
            )
            portfolio.save()
            messages.success(request, "Trade added successfully!")
            return redirect('portfolio:index')
    else:
        form = TradeForm()
    return render(request, 'portfolio/add_trade.html', {'form': form})

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

def trasaction_view(request):
    #user_id = request.POST.get('user_id')
    #stock_id = request.POST.get('stock_id')

    user_id = 2;
    stock_id = 5;

    transactions = Portfolio.objects.filter(user_id=user_id, stock_id=stock_id).order_by('-transactionDate')
    print(transactions);
    print(transactions.first().portfolioId);
    return render(request, 'portfolio/transaction.html', {'transactions': transactions})

@require_POST
def delete_transaction(request, transaction_id):
    try:
        txn = Portfolio.objects.get(portfolioId=transaction_id)
        
        txn.delete()
        return JsonResponse({"success": True})
    except Portfolio.DoesNotExist:
        return JsonResponse({"success": False, "error": "Transaction not found"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})
