from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsWaiter(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'waiter'


class IsBarman(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'barman'


class IsKitchen(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'kitchen'


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            'admin', 'waiter', 'barman', 'kitchen'
        ]
```
