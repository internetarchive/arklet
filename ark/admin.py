from django.contrib import admin

from ark.models import User, Naan, Shoulder, Ark, Key


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


@admin.register(Key)
class KeyAdmin(admin.ModelAdmin):
    list_display = ["key", "naan", "active"]
