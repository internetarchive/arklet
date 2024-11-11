import hashlib
import uuid
from typing import Union

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models
from django.db.models import Q, UniqueConstraint

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


class APIKeyManager(models.Manager):
    """Default Manager for the APIKey model."""

    def create_key(self, naan: Naan, name: str) -> str:
        """Create a new APIKey instance for the given Naan. Naans are required to
        give each APIKey they create a name. This method returns the plaintext API
        key, but ensures the key is hashed before saving to the database.

        It is the caller's responsibility to ensure the original plain_key is saved.
        We cannot infer the plain_key from the hashed key saved to the database.
        """
        plain_key = str(uuid.uuid4())
        hashed_key = self.hash_key(plain_key)
        self.create(key=hashed_key, key_prefix=plain_key[:6], naan=naan, name=name)
        return plain_key

    def get_by_plain_key(self, plain_key: Union[str, bytes]):
        """Lookup the APIKey by its plaintext key. Hashing is performed by the
        manager prior to lookup. Accepts str or utf-8/latin-1/ascii bytes."""
        hashed_key = self.hash_key(plain_key)
        return self.select_related("naan").get(key=hashed_key, is_active=True)

    @staticmethod
    def hash_key(plain_key: Union[str, bytes]):
        """SHA256 hash the plaintext API key. Accepts str or utf-8/latin-1/ascii.
        Yes, a single SHA256 is sufficient because UUID4 is high entropy. The key is
        re-hashed on every API call, so we don't want expensive, unnecessary iteration.
        """
        if isinstance(plain_key, str):
            plain_key = plain_key.encode()
        elif not isinstance(plain_key, bytes):
            raise TypeError("plain_key must be of type str or bytes")

        return hashlib.sha256(plain_key).hexdigest()


class APIKey(models.Model):
    """API keys for ARK minters. Keys are generated as UUID4. They are sha256 hashed
    before they are saved to the database (hashing once is enough for UUID4). Always use
    APIKeyManager methods for creating and looking-up keys, as these will handle the
    hashing steps for you."""

    key = models.CharField(max_length=64, unique=True, editable=False)
    key_prefix = models.CharField(max_length=6, editable=False)
    naan = models.ForeignKey(Naan, on_delete=models.CASCADE, related_name="api_keys")
    name = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = APIKeyManager()

    class Meta:
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"
        constraints = [
            UniqueConstraint(
                fields=["naan", "name"],
                condition=Q(is_active=True),
                name="unique_key_name_for_naan",
            ),
        ]

    def __str__(self):
        return self.name


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
