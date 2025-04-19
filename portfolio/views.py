from django.shortcuts import render, redirect
from django.contrib import messages
from userAuth.decorators import login_required_custom
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .forms import TradeForm
from .models import Trade
from .utils import PortfolioService, validate_transaction_for_edit_or_delete, delete_subsequent_transactions

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
        txns = Trade.objects.filter(stock_id=stockId, user=request.myuser.user_id)
        txns.delete()
        messages.success(request, "Stock deleted successfully!")
    return redirect('portfolio:index')

def add_trade(request):
    print("Add Request received")
    if request.method == 'POST':
        print("POST request received")
        form = TradeForm(request.POST)
        userId = request.myuser.user_id
        try: 
            if form.is_valid():
                stock = form.cleaned_data['stock']
                stockQty = form.cleaned_data['quantity']
                transactionPrice = form.cleaned_data['trade_price']
                transactionType = form.cleaned_data['direction']
                transactionDate = form.cleaned_data['date']
                trades = []

                trade = Trade(
                    user=request.myuser,
                    stock=stock,
                    quantity=stockQty,
                    trade_price=transactionPrice,
                    direction=transactionType,
                    date=transactionDate,
                    quantity_before = PortfolioService(userId).GetQuantityBefore(stock.stock_id,transactionDate,transactionType)
                )

                trades.append(trade)

                if transactionType == 'B' or validate_transaction_for_edit_or_delete(trades,'ADD'):
                    trade.save()
                    delete_subsequent_transactions(trade)

                messages.success(request, "Trade added successfully!")
                return redirect('portfolio:index')
        except Exception as e:
            print("Error:", str(e))
            messages.error(request, f"Error: {str(e)}")
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

def transaction_view(request,stock_id):

    print("Transaction View Request received")
    user_id = request.myuser.user_id

    transactions = Trade.objects.filter(user_id=user_id, stock_id=stock_id).order_by('-date','-trade_id')
    print(transactions)
    return render(request, 'portfolio/transaction.html', {'transactions': transactions})

@require_POST
def delete_transaction(request, transaction_id):
    try:
        trd = Trade.objects.get(trade_id=transaction_id)
        trades = [trd]
        if trd.direction == 'S' or validate_transaction_for_edit_or_delete(trades,'DELETE'): 
            pk = trd.trade_id 
            trd.delete()
            trd.trade_id = pk
            delete_subsequent_transactions(trd)
        else:
            raise Exception("Cannot delete as further transactions affected.")
        return JsonResponse({"success": True})
    except Trade.DoesNotExist:
        return JsonResponse({"success": False, "error": "Transaction not found"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})
