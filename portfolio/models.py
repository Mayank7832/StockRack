from django.db import models
from django.db.models import Q, F, CheckConstraint
from django.db.models.functions import TruncDate
from django.contrib.auth.hashers import make_password,check_password

# Create your models here.
class Stock(models.Model):
    class Meta:
        constraints = [
            CheckConstraint(
                check=Q(price__gt=0),
                name="stock_price_positive_constraint"
            )
        ]

    stock_id = models.AutoField(db_column="stk_id", primary_key=True)
    stock_name = models.CharField(db_column="stk_name", max_length=50, unique=True)
    script_code = models.CharField(db_column="stk_script_code", max_length=20, unique=True)
    price = models.DecimalField(db_column="stk_price", max_digits=9, decimal_places=2)
    created_on = models.DateTimeField(db_column="created_on", auto_now_add=True)
    updated_on = models.DateTimeField(db_column="updated_on", auto_now=True)

    def __str__(self):
        return " | ".join((self.stock_name, str(self.price)))
    
class User(models.Model):
    user_id = models.AutoField(db_column="usr_id", primary_key=True)
    name = models.CharField(db_column="usr_name", max_length = 100)
    email_id = models.EmailField(db_column="usr_email_id", unique=True)
    password = models.CharField(db_column="usr_password", max_length=128)
    created_on = models.DateTimeField(db_column="created_on", auto_now_add=True)
    updated_on = models.DateTimeField(db_column="updated_on", auto_now = True)

    def __str__(self):
        return " | ".join((str(self.user_id), 
                           self.name, 
                           self.email_id))
    
    def save(self, *args, **kwargs):
        self.password = make_password(self.password)  # Hash before saving
        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

class Trade(models.Model):
    class Meta:
        constraints = [
            CheckConstraint(
                check=~Q(direction='S') | Q(quantity_before__gte=F('quantity')),
                name="trade_sell_quantity_valid_constraint"
            ),
            CheckConstraint(
                check=Q(date__lte=TruncDate(F('created_on'))),
                name="trade_date_not_in_future_constraint"
            ),
            CheckConstraint(
                check=Q(trade_price__gt=0),
                name="trade_price_positive_constraint"
            ),
            CheckConstraint(
                check=Q(quantity__gt=0),
                name="trade_quantity_positive_constraint"
            )
        ]

    TRANSACTION_TYPE = [
        ('B', 'Buy'),
        ('S', 'Sell'),
        # A sequence of 2-value tuples to use as choices for a field.
        # The first element in each tuple is the value that will be stored in the database.
        # The second element is displayed by the field's form widget.
    ]

    trade_id = models.AutoField(db_column="trd_id", primary_key=True)
    user = models.ForeignKey(User, db_column="trd_usr_id", on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, db_column="trd_stk_id", on_delete=models.CASCADE)
    quantity = models.IntegerField(db_column="trd_qty")
    direction = models.CharField(db_column="trd_dir", max_length=1, choices=TRANSACTION_TYPE)
    trade_price = models.DecimalField(db_column="trd_price", max_digits=9, decimal_places=2)
    date = models.DateField(db_column="trd_date")
    quantity_before = models.IntegerField(db_column="trd_qty_before", default=0)
    #quantity_after = models.IntegerField(db_column="trd_qty_after")
    created_on = models.DateTimeField(db_column="created_on", auto_now_add=True)
    updated_on = models.DateTimeField(db_column="updated_on", auto_now=True)
    
    def __str__(self):
        return " | ".join((str(self.trade_id), 
                           self.user.name, 
                           self.stock.stock_name, 
                           self.direction, 
                           str(self.quantity)))

