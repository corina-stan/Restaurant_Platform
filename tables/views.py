from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils import timezone
from .models import Table, QRSession
from .serializers import QRSessionSerializer
from accounts.permissions import IsStaff


def run_auto_migrations():
    try:
        from django.core.management import call_command
        call_command('makemigrations')
        call_command('migrate')
        
        # Backfill existing invoices
        from menu.models import PurchaseInvoice
        invoices = PurchaseInvoice.objects.filter(nir_number__isnull=True).order_by('id')
        if invoices.exists():
            from django.db.models import Max
            max_nir = PurchaseInvoice.objects.aggregate(Max('nir_number'))['nir_number__max'] or 0
            for idx, inv in enumerate(invoices):
                inv.nir_number = max_nir + idx + 1
                inv.save()
    except Exception as e:
        print("Auto-migrations error:", e)


class ScanQRView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, table_number):
        run_auto_migrations()
        try:
            table = Table.objects.get(number=table_number, is_active=True)
        except Table.DoesNotExist:
            return Response(
                {'error': 'Masa nu există sau nu este activă.'},
                status=status.HTTP_404_NOT_FOUND
            )

        session = QRSession.objects.filter(
            table=table,
            is_active=True
        ).first()

        if not session:
            session = QRSession.objects.create(table=table)

        return Response({
            'session_token': str(session.token),
            'table_number': table.number,
            'table_name': table.name,
        }, status=status.HTTP_200_OK)

class ValidateQRView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        run_auto_migrations()
        try:
            session = QRSession.objects.get(token=token, is_active=True)
            return Response({
                'valid': True,
                'table_number': session.table.number,
                'session_token': str(session.token),
            })
        except QRSession.DoesNotExist:
            return Response(
                {'valid': False, 'error': 'Sesiune invalidă sau expirată.'},
                status=status.HTTP_404_NOT_FOUND
            )

class AllTablesView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        run_auto_migrations()
        from .serializers import TableSerializer
        tables = Table.objects.filter(is_active=True).order_by('number')
        return Response(TableSerializer(tables, many=True).data)


class CallWaiterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, table_number):
        session = QRSession.objects.filter(table__number=table_number, is_active=True).first()
        if not session:
            return Response({'error': 'Nu există o sesiune activă pentru această masă.'}, status=status.HTTP_400_BAD_REQUEST)
        
        session.waiter_called = True
        session.save()

        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'waiters',
            {
                'type': 'assistance_requested',
                'table_number': table_number,
                'message': f'Masa {table_number} solicită asistență!'
            }
        )
        return Response({'success': True, 'message': 'Ospătarul a fost chemat.'}, status=status.HTTP_200_OK)


class RequestBillView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, table_number):
        session = QRSession.objects.filter(table__number=table_number, is_active=True).first()
        if not session:
            return Response({'error': 'Nu există o sesiune activă pentru această masă.'}, status=status.HTTP_400_BAD_REQUEST)
        
        payment_method = request.data.get('payment_method', 'cash')
        tip_val = request.data.get('tip', 0)
        group_name = request.data.get('group_name')
        group_id = request.data.get('group_id')
        
        from decimal import Decimal
        try:
            tip = Decimal(str(tip_val))
        except Exception:
            tip = Decimal('0.00')

        session.bill_requested = True
        session.bill_payment_method = payment_method
        session.bill_tip = tip
        session.save()

        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'waiters',
            {
                'type': 'bill_requested',
                'table_number': table_number,
                'payment_method': payment_method,
                'tip': float(tip),
                'group_name': group_name,
                'group_id': group_id,
                'message': f'Masa {table_number} ({group_name or "Toată masa"}) solicită nota de plată ({payment_method}) cu bacșiș {tip} lei!'
            }
        )
        return Response({'success': True, 'message': 'Nota de plată a fost solicitată.'}, status=status.HTTP_200_OK)


class DismissNotificationView(APIView):
    permission_classes = [IsStaff]

    def post(self, request, table_number):
        session = QRSession.objects.filter(table__number=table_number, is_active=True).first()
        if not session:
            return Response({'error': 'Nu există o sesiune activă pentru această masă.'}, status=status.HTTP_400_BAD_REQUEST)
        
        session.waiter_called = False
        session.bill_requested = False
        session.save()

        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'waiters',
            {
                'type': 'new_order',
                'table_number': table_number,
                'order_id': None
            }
        )
        return Response({'success': True, 'message': 'Notificările au fost șterse.'}, status=status.HTTP_200_OK)