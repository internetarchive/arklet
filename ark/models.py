import uuid

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models

from ark.utils import generate_noid, noid_check_digit


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


class ArkManager(models.Manager):
    def mint(self, naan, shoulder, url, metadata, commitment):
        ark, collisions = None, 0
        for _ in range(10):
            noid = generate_noid(8)
            base_ark_string = f"{naan.naan}{shoulder}{noid}"
            check_digit = noid_check_digit(base_ark_string)
            ark_string = f"{base_ark_string}{check_digit}"
            try:
                ark = self.create(
                    ark=ark_string,
                    naan=naan,
                    shoulder=shoulder,
                    assigned_name=f"{noid}{check_digit}",
                    url=url,
                    metadata=metadata,
                    commitment=commitment,
                )
                break
            except IntegrityError:
                collisions += 1
                continue
        return ark, collisions


class Ark(models.Model):
    ark = models.CharField(primary_key=True, max_length=200, editable=False)
    naan = models.ForeignKey(Naan, on_delete=models.DO_NOTHING, editable=False)
    shoulder = models.CharField(max_length=50, editable=False)
    assigned_name = models.CharField(max_length=100, editable=False)
    url = models.URLField(default="", blank=True)
    metadata = models.TextField(default="", blank=True)
    commitment = models.TextField(default="", blank=True)

    objects = ArkManager()

    def clean(self):
        expected_ark = f"{self.naan.naan}{self.shoulder}{self.assigned_name}"
        if self.ark != expected_ark:
            raise ValidationError(f"expected {expected_ark} got {self.ark}")

    def __str__(self):
        return f"ark:/{self.ark}"
