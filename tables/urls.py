from django.urls import path
from . import views

urlpatterns = [
    path('scan/<int:table_number>/', views.ScanQRView.as_view(), name='scan_qr'),
    path('validate/<str:token>/', views.ValidateQRView.as_view(), name='validate_qr'),
]