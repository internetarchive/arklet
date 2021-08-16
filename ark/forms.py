from django import forms
from django.core.exceptions import ValidationError

from ark.utils import parse_ark


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
