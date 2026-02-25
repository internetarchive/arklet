from django import forms
from django.core.exceptions import ValidationError

from arklet.ark.models import Ark, Naan
from arklet.ark.utils import parse_ark


def validate_shoulder(shoulder: str):
    if not shoulder.startswith("/"):
        raise ValidationError("Shoulders must start with a forward slash")


def validate_ark(ark: str):
    try:
        parse_ark(ark)
    except ValueError as e:
        raise ValidationError(f"Invalid ARK: {e}")


class MintArkForm(forms.Form):
    naan = forms.IntegerField()
    shoulder = forms.CharField(validators=[validate_shoulder])
    url = forms.URLField(required=False)
    metadata = forms.CharField(required=False)
    commitment = forms.CharField(required=False)


class UpdateArkForm(forms.Form):
    ark = forms.CharField(validators=[validate_ark])
    url = forms.URLField(required=False)
    metadata = forms.CharField(required=False)
    commitment = forms.CharField(required=False)


class MintArkAdminForm(forms.ModelForm):
    """Form used in the Django admin to mint a new ARK.

    The naan and shoulder fields drive the ArkManager.mint() call; the
    remaining fields (url, metadata, commitment) are passed through directly.
    """

    naan = forms.ModelChoiceField(
        queryset=None,  # set in __init__ to avoid import-time query
        help_text="The Name Assigning Authority Number for this ARK.",
    )
    shoulder = forms.CharField(
        validators=[validate_shoulder],
        help_text="Shoulder string, e.g. /s1. Must start with a forward slash.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["naan"].queryset = Naan.objects.all()

    class Meta:
        model = Ark
        fields = ["url", "metadata", "commitment"]
