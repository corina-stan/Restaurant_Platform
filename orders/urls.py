from django.urls import path
from . import views

urlpatterns = [
    path('', views.AllOpenOrdersView.as_view(), name='all_orders'),
    path('create/', views.CreateOrderView.as_view(), name='create_order'),
    path('<int:order_id>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('table/<int:table_number>/', views.TableOrdersView.as_view(), name='table_orders'),
    path('items/<int:item_id>/status/', views.UpdateOrderItemStatusView.as_view(), name='update_item_status'),
    path('groups/', views.CreateOrderGroupView.as_view(), name='create_group'),
    path('init/', views.CreateEmptyOrderView.as_view(), name='init_order'),
    path('reports/', views.AdminReportsView.as_view(), name='admin_reports'),
    path('operation-logs/', views.AdminOperationLogsView.as_view(), name='admin_operation_logs'),
]