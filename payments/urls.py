from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.CreatePaymentView.as_view(), name='create_payment'),
    path('order/<int:order_id>/', views.OrderPaymentsView.as_view(), name='order_payments'),
    path('shift-report/', views.ShiftReportView.as_view(), name='shift_report'),
    path('recent/', views.RecentPaymentsView.as_view(), name='recent_payments'),
    path('z-report/create/', views.CreateZReportView.as_view(), name='create_z_report'),
]