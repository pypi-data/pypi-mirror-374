from django.contrib.auth.models import User
from django.http import HttpRequest


class PaymentMethodPermission:
    def is_permitted(
        self,
        request: HttpRequest | None = None,
        user: User | None = None,
    ) -> bool:
        raise NotImplementedError("Class must implement is_method_permitted(request=None, user=None)")


class Public(PaymentMethodPermission):
    def is_permitted(
        self,
        request: HttpRequest | None = None,
        user: User | None = None,
    ) -> bool:
        return True


class StaffOnly(PaymentMethodPermission):
    def is_permitted(
        self,
        request: HttpRequest | None = None,
        user: User | None = None,
    ) -> bool:
        return user is not None and user.is_authenticated and user.is_staff


class CustomerOnly(PaymentMethodPermission):
    def is_permitted(
        self,
        request: HttpRequest | None = None,
        user: User | None = None,
    ) -> bool:
        return user is None or not user.is_authenticated or (user.is_authenticated and not user.is_staff)
