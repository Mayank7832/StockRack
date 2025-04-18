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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stock'].empty_label = "Select a stock"
        self.fields['stock'].label_from_instance = lambda obj: f"{obj.stock_name}"