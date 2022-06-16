"""Django Admin models for Arklet."""

from django.contrib import admin

from ark.models import Ark, Key, Naan, Shoulder, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Django Admin model for ARK admin users."""


@admin.register(Naan)
class NaanAdmin(admin.ModelAdmin):
    """Django Admin model for Name Assignment Authority Number bearing organizations."""

    list_display = ["name", "naan"]


@admin.register(Shoulder)
class ShoulderAdmin(admin.ModelAdmin):
    """Django Admin model for ARK shoulders."""

    list_display = ["shoulder", "name", "naan"]


@admin.register(Ark)
class ArkAdmin(admin.ModelAdmin):
    """Django Admin model for ARKs.

    In practice, stock Django Admin doesn't work well for large randomly sorted tables.
    This view will tend to take a long time to load as a full table count query is run.
    """

    list_display = ["ark", "url"]
    show_full_result_count = False


@admin.register(Key)
class KeyAdmin(admin.ModelAdmin):
    """Django Admin model for managing Arklet access keys.

    These access keys are used to mint and bind ARKs via the Arklet API.
    """

    list_display = ["key", "naan", "active"]
