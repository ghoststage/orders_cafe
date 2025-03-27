from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('ready', 'Готово'),
        ('paid', 'Оплачено'),
    ]

    table_number = models.IntegerField(null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def update_total_price(self):
        self.total_price = sum(item.price for item in self.items.all())
        self.save()

    def __str__(self):
        return f"Order {self.id} - Table {self.table_number} - {self.status}"




class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=100, verbose_name="Название блюда")
    price = models.FloatField(verbose_name="Цена")

    def __str__(self):
        return f"{self.name} - {self.price} тнг."

class Dish(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название блюда")
    description = models.TextField(verbose_name="Описание", blank=True)
    price = models.FloatField(verbose_name="Цена")

    def __str__(self):
        return self.name

@receiver(post_save, sender=OrderItem)
@receiver(post_delete, sender=OrderItem)

def update_order_total(sender, instance, **kwargs):
    instance.order.update_total_price()