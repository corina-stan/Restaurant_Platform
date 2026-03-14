from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/table/(?P<table_number>\d+)/$', consumers.TableConsumer.as_asgi()),
    re_path(r'ws/kitchen/$', consumers.KitchenConsumer.as_asgi()),
    re_path(r'ws/bar/$', consumers.BarConsumer.as_asgi()),
    re_path(r'ws/waiters/$', consumers.WaiterConsumer.as_asgi()),
]