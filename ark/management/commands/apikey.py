from django.core.management.base import BaseCommand

from ark.models import APIKey, Naan


class Command(BaseCommand):
    """Create APIKey object and return the plaintext key before hashing to DB."""

    help = "Mint ARKs in bulk"

    def add_arguments(self, parser):
        parser.add_argument("naan", type=int)
        parser.add_argument("name", type=str)

    def handle(self, *args, **options):
        naan = Naan.objects.get(pk=options["naan"])
        name = options["name"]

        plain_key = APIKey.objects.create_key(naan, name)
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created APIKey {plain_key}")
        )
