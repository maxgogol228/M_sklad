from django.urls import path
from . import views

urlpatterns = [
    path('migrate/', views.run_migrations, name='migrate'),
    path('orders/<int:order_id>/receive/', views.mark_order_received, name='mark_received'),
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('devices/<int:device_id>/composition/', views.device_composition, name='device_composition'),
    path('logout/', views.logout_view, name='logout'),
    path('parts/', views.parts_list, name='parts_list'),
    path('parts/add/', views.part_add, name='part_add'),
    path('parts/edit/<int:part_id>/', views.part_edit, name='part_edit'),
    path('parts/delete/<int:part_id>/', views.part_delete, name='part_delete'),
    path('devices/', views.devices_list, name='devices_list'),
    path('devices/add/', views.device_add, name='device_add'),
    path('devices/edit/<int:device_id>/', views.device_edit, name='device_edit'),
    path('consumables/', views.consumables_list, name='consumables_list'),
    path('order/<int:part_id>/', views.create_order, name='create_order'),
    path('orders/', views.orders_list, name='orders_list'),
    path('reports/', views.reports, name='reports'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/create-key/', views.create_access_key, name='create_key'),
    path('admin-panel/logs/', views.view_logs, name='view_logs'),
    path('admin-panel/backup/', views.backup_database, name='backup'),
    path('admin-panel/make-admin/<int:user_id>/', views.make_admin, name='make_admin'),
]
