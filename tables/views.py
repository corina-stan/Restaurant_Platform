from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils import timezone
from .models import Table, QRSession
from .serializers import QRSessionSerializer


class ScanQRView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, table_number):
        try:
            table = Table.objects.get(number=table_number, is_active=True)
        except Table.DoesNotExist:
            return Response(
                {'error': 'Masa nu există sau nu este activă.'},
                status=status.HTTP_404_NOT_FOUND
            )

        QRSession.objects.filter(
            table=table,
            is_active=True
        ).update(is_active=False, closed_at=timezone.now())

        session = QRSession.objects.create(table=table)

        return Response({
            'session_token': str(session.token),
            'table_number': table.number,
            'table_name': table.name,
        }, status=status.HTTP_201_CREATED)


class ValidateQRView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
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