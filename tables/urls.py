from django.urls import path
from . import views

urlpatterns = [
    path('scan/<int:table_number>/', views.ScanQRView.as_view(), name='scan_qr'),
    path('validate/<str:token>/', views.ValidateQRView.as_view(), name='validate_qr'),
    path('all/', views.AllTablesView.as_view(), name='all_tables'),
    path('<int:table_number>/call_waiter/', views.CallWaiterView.as_view(), name='call_waiter'),
    path('<int:table_number>/request_bill/', views.RequestBillView.as_view(), name='request_bill'),
    path('<int:table_number>/dismiss_notification/', views.DismissNotificationView.as_view(), name='dismiss_notification'),
]