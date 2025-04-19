from django.db.models import IntegerField, Max, F, Q, Case, When, ExpressionWrapper
from .models import Trade
from collections import deque
from decimal import Decimal
from itertools import groupby

class PortfolioService:
    """
    Portfolio Service class to handle portfolio related operations.
    """

    def __init__(self, user):
        self.user = user
        self.user_trades = Trade.objects.filter(user=user)

    def fetch_user_trades(self):
        """
        Fetch transaction details for the user.
        """
        return (
            self.user_trades
            .select_related('stock')
            .values('stock__stock_name', 'quantity', 'trade_price', 'direction', 'date')
            .order_by('stock', 'date', 'trade_id')
        )

    def fetch_portfolio(self):
        """
        Fetch the portfolio of the user.
        """
        latest_trade_pks = (
            self.user_trades.values('stock')
            .annotate(latest_trade=Max('pk'))
            .values_list('latest_trade', flat=True)
        )

        direction_multiplier = Case(
            When(direction='B', then=1),
            When(direction='S', then=-1),
            output_field=IntegerField()
        )

        quantity_after_expr = ExpressionWrapper(
            F('quantity_before') + F('quantity') * direction_multiplier,
            output_field=IntegerField()
        )

        portfolio = (
            Trade.objects.filter(pk__in=latest_trade_pks)
            .select_related('stock')
            .annotate(quantity_after = quantity_after_expr)
            .filter(quantity_after__gt=0)
            .annotate(investment_value = F('stock__price') * quantity_after_expr)
        )

        trades = self.fetch_user_trades()
        print(trades)
        position_summaries = self.compute_portfolio_positions(trades)

        for pf_row in portfolio:
            pf_row.realized_profit = position_summaries[pf_row.stock.stock_name][0]
            pf_row.avg_price = position_summaries[pf_row.stock.stock_name][1]
            pf_row.holding_qty = position_summaries[pf_row.stock.stock_name][2]
            pf_row.investment_cost = pf_row.avg_price * pf_row.holding_qty
            pf_row.unrealized_profit = pf_row.investment_value - pf_row.investment_cost

        return portfolio

    def process_intraday_position(self, intraday_buys, intraday_sells):

        intraday_profit_loss = Decimal('0.0')

        while intraday_buys and intraday_sells:
            buy_trade = intraday_buys[0]
            sell_trade = intraday_sells[0]

            qty_to_square_off = min(buy_trade['qty'], sell_trade['qty'])
            intraday_profit_loss += (sell_trade['price'] - buy_trade['price']) * qty_to_square_off

            buy_trade['qty'] -= qty_to_square_off
            sell_trade['qty'] -= qty_to_square_off

            if buy_trade['qty'] == 0:
                intraday_buys.popleft()
            if sell_trade['qty'] == 0:
                intraday_sells.popleft()
        
        return intraday_profit_loss

    def compute_stock_positions(self, transactions):
        """
        Calculate the following for a list of transactions for a particular stock:
            1. Realized profit/loss
            2. Average buy price of the holding shares/quantity
            3. Total quantity of shares held
        
        The transactions are expected to be sorted by date and sequence of their execution.
        The calculations are performed in FIFO order.

        Note: Short selling is only allowed if squared off intraday.
        """

        # Dictionary to store transactions by date in sequence
        realized_profit = Decimal('0.0')
        global_queue = deque()
        intraday_buys = deque()
        intraday_sells = deque()
        trades_by_date = {
            txn_date: list(txn_group) for txn_date, txn_group in groupby(transactions, lambda txn: txn['date'])
        }

        for _, day_trades in trades_by_date.items():

            for trade in day_trades:
                if trade['direction'] == 'B':
                    intraday_buys.append({'qty': trade['quantity'], 'price': trade['trade_price']})
                else:
                    intraday_sells.append({'qty': trade['quantity'], 'price': trade['trade_price']})
                    
            intraday_profit_loss = self.process_intraday_position(intraday_buys, intraday_sells)
            realized_profit += intraday_profit_loss

            while intraday_buys:
                global_queue.append(intraday_buys.popleft())

            while intraday_sells and global_queue:
                buy_trade_global = global_queue[0]
                sell_trade = intraday_sells[0]

                qty_to_sell = min(buy_trade_global['qty'], sell_trade['qty'])
                realized_profit += (sell_trade['price'] - buy_trade_global['price']) * qty_to_sell

                buy_trade_global['qty'] -= qty_to_sell
                sell_trade['qty'] -= qty_to_sell

                if buy_trade_global['qty'] == 0:
                    global_queue.popleft()
                if sell_trade['qty'] == 0:
                    intraday_sells.popleft()

            if intraday_sells:
                raise ValueError("No more shares to sell.")

        total_qty = sum(item['qty'] for item in global_queue)
        avg_buy_price = (
            sum(item['qty'] * item['price'] for item in global_queue) / total_qty
            if total_qty > 0 else Decimal('0.0')
        )
        
        return (realized_profit, avg_buy_price, total_qty)

    def compute_portfolio_positions(self, transactions):
        
        trades_by_stock = {
            name: list(trades_per_stock)
            for name, trades_per_stock in groupby(transactions, lambda txn: txn['stock__stock_name'])
        }
        
        for name, txns in trades_by_stock.items():
            trades_by_stock[name] = self.compute_stock_positions(txns)

        return trades_by_stock

    
    def GetQuantityBefore(self,stock_id,date,direction):
        quantity_before = 0
        priorTrade = (
            self.user_trades.filter(
            stock_id=stock_id,
            date__lte=date
            )
            .order_by('-date', '-trade_id')
            .first()
        )
        print("Prior Trade:", priorTrade)

        if priorTrade is None and direction == 'S':
            raise Exception("Cannot sell as no prior buy transaction found.")
        elif priorTrade is None: return 0

        if priorTrade.direction == 'B':
            quantity_before = priorTrade.quantity_before + priorTrade.quantity
        else:
            quantity_before = priorTrade.quantity_before - priorTrade.quantity

        return quantity_before
    
def validate_transaction_for_edit_or_delete(trades, operation):
    print(f"Validating transaction for operation: {operation}")
    try:
        if not trades:
            return False  
        
        if operation == 'DELETE':
            trade = Trade.objects.get(trade_id=trades[0].trade_id)
            if trade.quantity_before <= 0:
                print(f"Cannot delete: available quantity would become less than 0. Trade ID: {trade.trade_id}")
                return False
        
        elif operation == 'EDIT':
            trade = trades[0]
            if get_quantity_after(trade) < 0:
                print(f"Cannot edit: available quantity would become less than 0. Trade ID: {trade.trade_id}")
                return False
        
        elif operation == 'ADD':
            stocks_processed = {}

            for trade in trades:
                stock_name = trade.stock.stock_name
                trade_date = trade.date

                if stock_name in stocks_processed:
                    if stocks_processed[stock_name] != trade_date:
                        raise Exception(f"Multiple dates for stock: {stock_name}. First date: {stocks_processed[stock_name]}, Second date: {trade_date}")
                    else:
                        continue
                else:
                    stocks_processed[stock_name] = trade_date

                prior_trade = Trade.objects.filter(
                    user_id=trade.user_id,
                    stock_id=trade.stock_id,
                    date__lte=trade.date
                ).order_by('-date', '-trade_id').first()

                net_quantity_before_new_trades = get_quantity_after(prior_trade) if prior_trade else 0
                net_quantity_after_new_trades = sum(
                    t.quantity if t.direction == 'B' else -t.quantity
                    for t in trades
                    if t.stock.stock_name == stock_name
                )

                if net_quantity_before_new_trades + net_quantity_after_new_trades < 0:
                    print(f"Cannot add: available quantity would become less than 0. Stock: {stock_name}")
                    return False
        else:
            print(f"Unsupported operation: {operation}")
            return False

        return True
    
    except Trade.DoesNotExist:
        print("Trade does not exist.")
        return None
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        return None
        
def delete_subsequent_transactions(trade):
        try:
            trades = Trade.objects.filter(
                user_id=trade.user_id,
                stock_id=trade.stock_id,
                date__gte=trade.date
            )
            
            if trades.exists():
                trades_to_delete = trades.filter(
                    Q(date__gt=trade.date) | Q(date=trade.date, trade_id__gt=trade.trade_id)
                )

                trades_to_delete.delete()
            return True  
        
        except Exception as e:
            print(f"Error deleting subsequent trades: {e}")
            raise Exception(e)
        
def get_quantity_after(trade):
    if trade.direction == 'B':
        return trade.quantity_before + trade.quantity
    else:
        return trade.quantity_before - trade.quantity
        

