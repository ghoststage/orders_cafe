from django.urls import path
from . import views
from .views import order_list, search_orders, add_order, delete_order, update_status, calculate_revenue, add_item_to_order, delete_item_from_order, edit_order, api_orders, api_order_detail, add_dish, dish_list


urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('search/', views.search_orders, name='search_orders'),
    path('add/', views.add_order, name='add_order'),
    path('delete/<int:order_id>/', views.delete_order, name='delete_order'),
    path('update_status/<int:order_id>/<str:new_status>/', views.update_status, name='update_status'),
    path('revenue/', views.calculate_revenue, name='calculate_revenue'),
    path('order/<int:order_id>/add_item/', views.add_item_to_order, name='add_item_to_order'),
    path('order/<int:order_id>/item/<int:item_id>/delete/', views.delete_item_from_order,
         name='delete_item_from_order'),
    path('order/<int:order_id>/edit/', views.edit_order, name='edit_order'),
    path('add_dish/', add_dish, name='add_dish'),
    path('dish_list/', dish_list, name='dish_list'),

    # API маршруты
    path('api/orders/', views.api_orders, name='api_orders'),
    path('api/orders/<int:order_id>/', views.api_order_detail, name='api_order_detail'),


]
