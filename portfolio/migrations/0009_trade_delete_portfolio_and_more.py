# Generated by Django 5.1.7 on 2025-04-14 14:49

import django.db.models.deletion
import django.db.models.functions.datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0008_rename_stock_portfolio_stockid_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Trade',
            fields=[
                ('trade_id', models.AutoField(db_column='trd_id', primary_key=True, serialize=False)),
                ('quantity', models.IntegerField(db_column='trd_qty')),
                ('direction', models.CharField(choices=[('B', 'Buy'), ('S', 'Sell')], db_column='trd_dir', max_length=1)),
                ('trade_price', models.DecimalField(db_column='trd_price', decimal_places=2, max_digits=9)),
                ('date', models.DateField(db_column='trd_date')),
                ('quantity_before', models.IntegerField(db_column='trd_qty_before', default=0)),
                ('created_on', models.DateTimeField(auto_now_add=True, db_column='created_on')),
                ('updated_on', models.DateTimeField(auto_now=True, db_column='updated_on')),
                ('stock', models.ForeignKey(db_column='trd_stk_id', on_delete=django.db.models.deletion.CASCADE, to='portfolio.stock')),
                ('user', models.ForeignKey(db_column='trd_usr_id', on_delete=django.db.models.deletion.CASCADE, to='portfolio.user')),
            ],
        ),
        migrations.DeleteModel(
            name='Portfolio',
        ),
        migrations.AddConstraint(
            model_name='trade',
            constraint=models.CheckConstraint(condition=models.Q(models.Q(('direction', 'S'), _negated=True), ('quantity_before__gte', models.F('quantity')), _connector='OR'), name='trade_sell_quantity_valid_constraint'),
        ),
        migrations.AddConstraint(
            model_name='trade',
            constraint=models.CheckConstraint(condition=models.Q(('date__lte', django.db.models.functions.datetime.TruncDate(models.F('created_on')))), name='trade_date_not_in_future_constraint'),
        ),
        migrations.AddConstraint(
            model_name='trade',
            constraint=models.CheckConstraint(condition=models.Q(('quantity__gt', 0)), name='trade_quantity_positive_constraint'),
        ),
    ]
