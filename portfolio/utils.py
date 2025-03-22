from .models import Portfolio, Stock
from collections import deque, defaultdict
from decimal import Decimal

def FetchPortfolio(userId):
    """
    Fetch the portfolio of a user.
    """
    
    return (
        Portfolio.objects.filter(user_id=userId)
        .select_related('stock')
        .order_by('stock', 'transactionDate')
        .values_list('stock', 'stock__stockName', 'stockQty', 'transactionPrice', 'transactionType')
    )

def CalculatePnLFIFO(transactions):
    """
    Calculate profit/loss for a list of transactions.
    """

    queue = deque() # Stores (buyQty, buyPrice) for buy transactions
    totalProfit = Decimal('0.0')

    for txn in transactions:
        if txn['type'] == 'B':
            queue.append((txn['qty'], txn['price']))
        else:
            sellQty = txn['qty']
            sellPrice = txn['price']

            while sellQty > 0:
                buyQty, buyPrice = queue.popleft()
                qtyToSell = min(sellQty, buyQty)
                totalProfit += (sellPrice - buyPrice) * qtyToSell
                sellQty -= qtyToSell

                if buyQty > qtyToSell:
                    queue.appendleft((buyQty - qtyToSell, buyPrice))
    
    # Calculate unrealized profit for buy transactions left in queue

    return totalProfit

def CalculatePnL(portfolio):
    """
    """

    stockTxns = defaultdict(list)

    for stock, stockName, qty, price, txnType in portfolio:
        stockTxns[stockName].append({
            'qty': qty,
            'price': price,
            'type': txnType,
        })

    for stockName, txns in stockTxns.items():
        stockTxns[stockName] = CalculatePnLFIFO(txns)

    return stockTxns

def RetrievePortfolio(portfolio):
    pass

