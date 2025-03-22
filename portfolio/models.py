from django.db import models
from django.contrib.auth.hashers import make_password

# Create your models here.
class Stock(models.Model):
    stockId = models.AutoField(db_column="stk_id", primary_key=True)
    stockName = models.CharField(db_column="stk_name", max_length=50, unique=True)
    scriptCode = models.CharField(db_column="stk_script_code", max_length=20, unique=True)
    price = models.DecimalField(db_column="stk_price", max_digits=9, decimal_places=2)
    createdOn = models.DateTimeField(db_column="createdOn", auto_now_add=True)
    updatedOn = models.DateTimeField(db_column="updatedOn", auto_now=True)

    def __str__(self):
        return str({
            "StockId" : self.stockId,
            "StockName" : self.stockName,
            "StockPrice" : self.price,
        })
    
class User(models.Model):
    userId = models.AutoField(db_column="usr_id", primary_key=True)
    name = models.CharField(db_column="usr_name", max_length = 100)
    emailId = models.EmailField(db_column="usr_email_id", unique=True)
    password = models.CharField(db_column="usr_password", max_length=128)
    createdOn = models.DateTimeField(db_column="createdOn", auto_now_add=True)
    updatedOn = models.DateTimeField(db_column="updatedOn", auto_now = True)

    def __str__(self):
        return str({
            "UserId" :self.userId,
            "UserName" : self.name,
            "EmailId" : self.emailId,
            })
    
    def save(self, *args, **kwargs):
        self.password = make_password(self.password)  # Hash before saving
        super().save(*args, **kwargs)

class Portfolio(models.Model):
    TRANSACTION_TYPE = [
        ('B', 'Buy'),
        ('S', 'Sell'),
    ]

    portfolioId = models.AutoField(db_column="pof_id", primary_key=True)
    user = models.ForeignKey(User, db_column="pof_usr_id", on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, db_column="pof_stk_id", on_delete=models.CASCADE)
    stockQty = models.IntegerField(db_column="pof_stk_qty")
    transactionType = models.CharField(db_column="pof_tran_type", max_length=1, choices=TRANSACTION_TYPE)
    transactionPrice = models.DecimalField(db_column="pof_tran_price", max_digits=9, decimal_places=2)
    transactionDate = models.DateTimeField(db_column="pof_tran_date")
    runningQtyBefore = models.IntegerField(db_column="pof_run_qty_before")
    runningQtyAfter = models.IntegerField(db_column="pof_run_qty_after")
    createdOn = models.DateTimeField(db_column="createdOn", auto_now_add=True)
    updatedOn = models.DateTimeField(db_column="updatedOn", auto_now=True)
    
    def __str__(self):
        return str({
            "PortfolioId": self.portfolioId,
            "UserId": self.user.userId,
            "StockId": self.stock.stockId,
        })
