from django.contrib import admin

from ark.models import User, Naan, Shoulder, Ark, Key


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Naan)
class NaanAdmin(admin.ModelAdmin):
    pass


@admin.register(Shoulder)
class ShoulderAdmin(admin.ModelAdmin):
    pass


@admin.register(Ark)
class ArkAdmin(admin.ModelAdmin):
    pass


@admin.register(Key)
class KeyAdmin(admin.ModelAdmin):
    pass
