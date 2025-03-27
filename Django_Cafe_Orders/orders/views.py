from .models import Order, OrderItem
from .models import Dish
from .forms import DishForm
from django.db import models
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import OrderSerializer, OrderItemSerializer
from django.db.models import Sum


def order_list(request):
    status_filter = request.GET.get("status")

    orders = Order.objects.all().prefetch_related("items")
    if status_filter:
        orders = orders.filter(status=status_filter)

    for order in orders:
        new_total = sum(item.price for item in order.items.all())
        if order.total_price != new_total:
            order.total_price = new_total
            order.save(update_fields=["total_price"])

    dishes = Dish.objects.all()
    return render(request, "orders/order_list.html", {"orders": orders, "dishes": dishes})




def search_orders(request):
    query = request.GET.get('query', '')
    orders = Order.objects.filter(
        models.Q(table_number__icontains=query) | models.Q(status__icontains=query)
    )
    return render(request, 'orders/order_list.html', {'orders': orders})


def add_order(request):
    dishes = Dish.objects.all()

    if request.method == "POST":
        table_number = request.POST["table_number"]
        dish_id = request.POST["dish"]
        dish = Dish.objects.get(id=dish_id)

        order = Order.objects.create(table_number=table_number)
        order.items.create(name=dish.name, price=dish.price)

        return redirect("order_list")

    return render(request, "orders/add_order.html", {"dishes": dishes})


def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return redirect('order_list')


def update_status(request, order_id, new_status):
    order = get_object_or_404(Order, id=order_id)
    order.status = new_status
    order.save()
    return redirect('order_list')

def add_dish(request):
    if request.method == 'POST':
        form = DishForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dish_list')
    else:
        form = DishForm()
    return render(request, 'orders/add_dish.html', {'form': form})

def dish_list(request):
    dishes = Dish.objects.all()
    return render(request, 'orders/dish_list.html', {'dishes': dishes})


def calculate_revenue(request):
    revenue = Order.objects.filter(status='paid').aggregate(total=Sum('total_price'))['total'] or 0
    print(f"DEBUG: Общее количество оплаченных заказов: {Order.objects.filter(status='paid').count()}")
    print(f"DEBUG: Выручка = {revenue}")
    return render(request, 'orders/revenue_report.html', {'revenue': revenue})




def add_item_to_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        item_name = request.POST.get('item_name')
        item_price = float(request.POST.get('item_price', 0))
        OrderItem.objects.create(order=order, name=item_name, price=item_price)

        order.update_total_price()

        return redirect('order_list')
    return render(request, 'orders/add_item.html', {'order': order})




def delete_item_from_order(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id)
    order = item.order
    item.delete()
    order.update_total_price()
    return redirect('order_list')


def edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    dishes = Dish.objects.all()

    if request.method == "POST":
        if "add_item" in request.POST:
            dish_id = request.POST.get("dish_id")
            dish = get_object_or_404(Dish, id=dish_id)
            OrderItem.objects.create(order=order, name=dish.name, price=dish.price)

        elif "delete_item" in request.POST:
            item_id = request.POST.get("item_id")
            item = get_object_or_404(OrderItem, id=item_id)
            item.delete()

        order.update_total_price()
        return redirect("edit_order", order_id=order.id)

    return render(request, "orders/edit_order.html", {"order": order, "dishes": dishes})


# API для получения списка заказов и создания нового заказа
@api_view(['GET', 'POST'])
def api_orders(request):
    if request.method == 'GET':
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# API для работы с конкретным заказом
@api_view(['GET', 'PUT', 'DELETE'])
def api_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'GET':
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = OrderSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
