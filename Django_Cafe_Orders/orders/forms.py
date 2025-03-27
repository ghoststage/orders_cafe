from django import forms
from .models import Dish

class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ['name', 'description', 'price',]
        labels = {
            'name': 'Название блюда',
            'description': 'Описание',
            'price': 'Цена',
        }