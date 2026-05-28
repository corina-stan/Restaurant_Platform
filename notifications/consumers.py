import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from tables.models import QRSession


class TableConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.table_number = self.scope['url_route']['kwargs']['table_number']
        self.room_group_name = f'table_{self.table_number}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Conectat la masa {self.table_number}'
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def order_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'order_update',
            'order_id': event['order_id'],
            'item_id': event.get('item_id'),
            'status': event['status'],
            'product_name': event.get('product_name', ''),
            'message': event.get('message', '')
        }))

    async def notification(self, event):
        await self.send(text_data=json.dumps({
            'type': event['notification_type'],
            'message': event['message']
        }))

    async def product_availability(self, event):
        await self.send(text_data=json.dumps({
            'type': 'product_availability',
            'product_id': event['product_id'],
            'is_available': event['is_available'],
            'product_name': event['product_name'],
        }))

    async def payment_completed(self, event):
        await self.send(text_data=json.dumps({
            'type': 'payment_completed',
            'order_id': event['order_id'],
            'group_id': event.get('group_id'),
        }))


class KitchenConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'kitchen'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Conectat la bucătărie'
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def new_order_item(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_order_item',
            'order_id': event['order_id'],
            'item_id': event['item_id'],
            'product_name': event['product_name'],
            'product_id': event.get('product_id'),
            'quantity': event['quantity'],
            'table_number': event['table_number'],
            'notes': event.get('notes', ''),
            'timestamp': event['timestamp']
        }))

    async def item_status_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'item_status_update',
            'item_id': event['item_id'],
            'status': event['status']
        }))

    async def product_availability(self, event):
        await self.send(text_data=json.dumps({
            'type': 'product_availability',
            'product_id': event['product_id'],
            'is_available': event['is_available'],
            'product_name': event['product_name'],
        }))


class BarConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'bar'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Conectat la bar'
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def new_order_item(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_order_item',
            'order_id': event['order_id'],
            'item_id': event['item_id'],
            'product_id': event.get('product_id'),    # adaugă această linie
            'product_name': event['product_name'],
            'quantity': event['quantity'],
            'table_number': event['table_number'],
            'notes': event.get('notes', ''),
            'timestamp': event['timestamp']
        }))

    async def item_status_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'item_status_update',
            'item_id': event['item_id'],
            'status': event['status']
        }))

    async def product_availability(self, event):
        await self.send(text_data=json.dumps({
            'type': 'product_availability',
            'product_id': event['product_id'],
            'is_available': event['is_available'],
            'product_name': event['product_name'],
        }))


class WaiterConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'waiters'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Conectat la interfața ospătar'
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def item_ready(self, event):
        await self.send(text_data=json.dumps({
            'type': 'item_ready',
            'item_id': event['item_id'],
            'product_name': event['product_name'],
            'table_number': event['table_number'],
            'order_id': event['order_id']
        }))

    async def assistance_requested(self, event):
        await self.send(text_data=json.dumps({
            'type': 'assistance_requested',
            'table_number': event['table_number'],
            'message': event['message']
        }))

    async def bill_requested(self, event):
        await self.send(text_data=json.dumps({
            'type': 'bill_requested',
            'table_number': event['table_number'],
            'payment_method': event['payment_method'],
            'tip': event['tip'],
            'message': event['message'],
            'group_name': event.get('group_name'),
            'group_id': event.get('group_id'),
        }))
    
    async def new_order(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_order',
            'order_id': event['order_id'],
            'table_number': event['table_number'],

        }))
    
    async def product_availability(self, event):
        await self.send(text_data=json.dumps({
            'type': 'product_availability',
            'product_id': event['product_id'],
            'is_available': event['is_available'],
            'product_name': event['product_name'],
        }))
    
    async def item_status_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'item_status_update',
            'item_id': event['item_id'],
            'status': event['status'],
            'order_id': event['order_id'],
            'table_number': event['table_number'],
            'product_name': event['product_name'],
        }))

    async def payment_completed(self, event):
        await self.send(text_data=json.dumps({
            'type': 'payment_completed',
            'order_id': event['order_id'],
            'table_number': event['table_number'],
            'group_id': event.get('group_id'),
        }))