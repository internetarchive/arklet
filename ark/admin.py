from django.contrib import admin
from django.core.paginator import Paginator
from django.db import OperationalError, connection, transaction
from django.utils.functional import cached_property

from ark.models import User, Naan, Shoulder, Ark, Key


class TimeLimitedPaginator(Paginator):
    """
    Paginator that enforces a timeout on the count operation.
    If the operations times out, a fake bogus value is
    returned instead.

    Lifted from: https://web.archive.org/web/20210422225156/https://hakibenita.com/optimizing-the-django-admin-paginator
    """

    @cached_property
    def count(self):
        # We set the timeout in a db transaction to prevent it from
        # affecting other transactions.
        with transaction.atomic(), connection.cursor() as cursor:
            cursor.execute("SET LOCAL statement_timeout TO 1000;")
            try:
                return super().count
            except OperationalError:
                return 9999999999


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Naan)
class NaanAdmin(admin.ModelAdmin):
    list_display = ["name", "naan"]


@admin.register(Shoulder)
class ShoulderAdmin(admin.ModelAdmin):
    list_display = ["shoulder", "name", "naan"]


@admin.register(Ark)
class ArkAdmin(admin.ModelAdmin):
    list_display = ["ark", "url"]
    show_full_result_count = False
    paginator = TimeLimitedPaginator


@admin.register(Key)
class KeyAdmin(admin.ModelAdmin):
    list_display = ["key", "naan", "active"]
