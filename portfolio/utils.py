from django.db.models import OuterRef, Subquery, Max, F
from .models import Portfolio, Stock
from collections import deque, defaultdict
from decimal import Decimal

class PortfolioService():
    """
    Portfolio Service class to handle portfolio related operations.
    """

    def __init__(self, userId):
        self.userId = userId
        self.userTxns = Portfolio.objects.filter(user_id=userId)

    def FetchUserTxnDetails(self):
        """
        Fetch transaction details for the user.
        """
        return (
            self.userTxns
            .select_related('stock')
            .order_by('stock', 'transactionDate')
            .values_list('stock', 'stock__stockName', 'stockQty', 'transactionPrice', 'transactionType')
        )

    def FetchPortfolio(self):
        """
        Fetch the portfolio of the user.
        """
        latestStockTxnSubquery = (
            self.userTxns.filter(stock=OuterRef('stock'))
            .order_by('-transactionDate')
            .values('pk')[:1]
        )

        userPortfolio = (
            Portfolio.objects.filter(pk__in=Subquery(latestStockTxnSubquery), runningQtyAfter__gt=0)
            .select_related('stock')
            .annotate(investmentValue = F('stock__price') * F('runningQtyAfter'))
        )

        userTxnDetails = self.FetchUserTxnDetails()
        realizedPnLAndAvgBuyPrice = self.FetchRealizedPnLAndAvgBuyPrice(userTxnDetails)

        for stockRecord in userPortfolio:
            stockRecord.avgBuyPrice = realizedPnLAndAvgBuyPrice.get(stockRecord.stock.stockName)[0]
            stockRecord.investmentCost = stockRecord.avgBuyPrice * stockRecord.runningQtyAfter
            stockRecord.realizedProfit = realizedPnLAndAvgBuyPrice.get(stockRecord.stock.stockName)[1]
            stockRecord.unrealizedProfit = stockRecord.investmentValue - stockRecord.investmentCost

        return userPortfolio

    def CalculateRealizedPnLAndAvgBuyPricePerStock(self, transactions):
        """
        Calculate realized profit/loss for a list of transactions for a particular stock.
            The transactions are expected to be sorted by date and the calculation is done in FIFO order.
        Also calculate the average buy price of the remaining shares.
        """

        queue = deque() # Stores (buyQty, buyPrice) for buy transactions
        realizedProfit = Decimal('0.0')

        for txn in transactions:
            if txn['type'] == 'B':
                queue.append((txn['qty'], txn['price']))
            else:
                sellQty = txn['qty']
                sellPrice = txn['price']

                while sellQty > 0:
                    buyQty, buyPrice = queue.popleft()
                    qtyToSell = min(sellQty, buyQty)
                    realizedProfit += (sellPrice - buyPrice) * qtyToSell
                    sellQty -= qtyToSell

                    if buyQty > qtyToSell:
                        queue.appendleft((buyQty - qtyToSell, buyPrice))
        
        avgBuyPrice = (
            sum(qty * price for qty, price in queue) / sum(qty for qty, _ in queue) 
            if queue else Decimal('0.0')
        )

        return avgBuyPrice, realizedProfit

    def FetchRealizedPnLAndAvgBuyPrice(self, portfolio):
        
        stockTxns = defaultdict(list)

        for stock, stockName, qty, price, txnType in portfolio:
            stockTxns[stockName].append({
                'qty': qty,
                'price': price,
                'type': txnType,
            })

        for stockName, txns in stockTxns.items():
            stockTxns[stockName] = self.CalculateRealizedPnLAndAvgBuyPricePerStock(txns)

        return stockTxns

