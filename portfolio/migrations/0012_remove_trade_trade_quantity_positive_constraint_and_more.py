# Generated by Django 5.1.7 on 2025-04-18 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0011_rename_emailid_user_email_id_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='trade',
            name='trade_quantity_positive_constraint',
        ),
        migrations.AlterField(
            model_name='stock',
            name='stock_name',
            field=models.CharField(db_column='stk_name', max_length=50, unique=True, verbose_name='STOCK NAME'),
        ),
        migrations.AlterField(
            model_name='trade',
            name='direction',
            field=models.CharField(choices=[('', 'Type'), ('B', 'BUY'), ('S', 'SELL')], db_column='trd_dir', max_length=1),
        ),
    ]
