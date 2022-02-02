import uuid

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class Naan(models.Model):
    naan = models.PositiveBigIntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    url = models.URLField()

    def __str__(self):
        return f"{self.name} - {self.naan}"


class User(AbstractUser):
    naan = models.ForeignKey(Naan, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return self.username


class Key(models.Model):
    key = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    naan = models.ForeignKey(Naan, on_delete=models.CASCADE)
    active = models.BooleanField()

    def __str__(self):
        return f"Key-{self.naan.naan}-{self.key.hex[:8]}..."


class Shoulder(models.Model):
    shoulder = models.CharField(max_length=50)
    naan = models.ForeignKey(Naan, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return f"{self.naan.naan}{self.shoulder}"


class Ark(models.Model):
    ark = models.CharField(primary_key=True, max_length=200, editable=False)
    naan = models.ForeignKey(Naan, on_delete=models.DO_NOTHING, editable=False)
    shoulder = models.CharField(max_length=50, editable=False)
    assigned_name = models.CharField(max_length=100, editable=False)
    url = models.URLField(default="", blank=True)
    metadata = models.TextField(default="", blank=True)
    commitment = models.TextField(default="", blank=True)

    def clean(self):
        expected_ark = f"{self.naan.naan}{self.shoulder}{self.assigned_name}"
        if self.ark != expected_ark:
            raise ValidationError(f"expected {expected_ark} got {self.ark}")

    def __str__(self):
        return f"ark:/{self.ark}"
