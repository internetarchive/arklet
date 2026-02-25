"""Django Admin models for Arklet."""

from django.contrib import admin, messages

from arklet.ark.forms import MintArkAdminForm
from arklet.ark.models import APIKey, Ark, Key, Naan, Shoulder, User


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

    The "Add ARK" action uses MintArkAdminForm so that staff can mint new ARKs through
    the admin instead of having to call the API directly.
    """

    list_display = ["ark", "url", "created_at", "updated_at"]
    show_full_result_count = False

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:  # add view – return the minting form directly to avoid
            # modelform_factory calling fields_for_model with 'naan', which raises
            # FieldError because Ark.naan is editable=False on the model.
            return MintArkAdminForm
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            naan = form.cleaned_data["naan"]
            shoulder = form.cleaned_data["shoulder"]
            url = form.cleaned_data.get("url", "")
            metadata = form.cleaned_data.get("metadata", "")
            commitment = form.cleaned_data.get("commitment", "")

            ark, collisions = Ark.objects.mint(naan, shoulder, url, metadata, commitment)

            if not ark:
                self.message_user(
                    request,
                    "Failed to mint ARK: too many NOID collisions.",
                    messages.ERROR,
                )
                return

            if collisions:
                self.message_user(
                    request,
                    f"ARK minted after {collisions} NOID collision(s).",
                    messages.WARNING,
                )

            # Populate obj so Django admin can redirect to the new change view.
            obj.ark = ark.ark
            obj.naan_id = ark.naan_id
            obj.shoulder = ark.shoulder
            obj.assigned_name = ark.assigned_name
            # ark is already saved by mint(); do NOT call obj.save() again.
        else:
            super().save_model(request, obj, form, change)


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    """Django Admin model for API Keys."""

    list_display = ["naan", "key_prefix", "name"]


@admin.register(Key)
class KeyAdmin(admin.ModelAdmin):
    """Django Admin model for managing Arklet access keys.

    These access keys are used to mint and bind ARKs via the Arklet API.
    """

    list_display = ["key", "naan", "active"]
