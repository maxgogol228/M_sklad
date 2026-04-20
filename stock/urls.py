from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('parts/', views.parts_list, name='parts_list'),
    path('parts/add/', views.part_add, name='part_add'),
    path('parts/edit/<int:part_id>/', views.part_edit, name='part_edit'),
    path('parts/delete/<int:part_id>/', views.part_delete, name='part_delete'),
    path('devices/', views.devices_list, name='devices_list'),
    path('devices/add/', views.device_add, name='device_add'),
    path('devices/edit/<int:device_id>/', views.device_edit, name='device_edit'),
    path('devices/<int:device_id>/composition/', views.device_composition, name='device_composition'),
    path('consumables/', views.consumables_list, name='consumables_list'),
    path('order/<int:part_id>/', views.create_order, name='create_order'),
    path('orders/', views.orders_list, name='orders_list'),
    path('orders/<int:order_id>/receive/', views.mark_order_received, name='mark_received'),
    path('reports/', views.reports, name='reports'),
    path('backup/', views.backup_database, name='backup'),
]
