from django import forms
from django.forms import ModelForm
from .models import Trade

class TradeForm(ModelForm):
    class Meta:
        model = Trade
        fields = ['stock', 'quantity', 'trade_price', 'direction', 'date']
        widgets = {
            'stock': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'trade_price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0.01}),
            'direction': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'trade_price': 'Price',
        }
    # def clean(self):
    #     cleaned_data = super().clean()
    #     quantity = cleaned_data.get('quantity')
    #     price = cleaned_data.get('price')

    #     if quantity <= 0:
    #         self.add_error('quantity', 'Quantity must be greater than zero.')
    #     if price <= 0:
    #         self.add_error('price', 'Price must be greater than zero.')

    #     return cleaned_data