from django import forms
from .models import Product, Order, OrderItem


class ProductForm(forms.ModelForm):
    """Form for creating and editing products"""
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'quantity_in_stock', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantity_in_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'quantity_in_stock': 'Quantity in Stock',
            'is_active': 'Active',
        }


class AddToCartForm(forms.ModelForm):
    """Form for adding products to cart"""
    class Meta:
        model = OrderItem
        fields = ['quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'style': 'width: 100px;',
                'min': '1',
                'value': '1'
            }),
        }
