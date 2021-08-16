from django.core.management.base import BaseCommand, CommandError

from ark.models import Ark, Naan
from ark.utils import generate_noid


class Command(BaseCommand):
    help = "Mint ARKs in bulk"

    def add_arguments(self, parser):
        parser.add_argument("ark_count", type=int)
        parser.add_argument("naan", type=int)
        parser.add_argument("shoulder", type=str)

    def handle(self, *args, **options):
        ark_count = options["ark_count"]
        naan_id = options["naan"]
        naan = Naan.objects.get(pk=options["naan"])
        shoulder = options["shoulder"]

        Ark.objects.bulk_create(
            Ark(
                ark=f"{naan_id}{shoulder}{generate_noid(20)}",
                naan=naan,
                shoulder=shoulder,
            )
            for _ in range(ark_count)
        )
        self.stdout.write(self.style.SUCCESS(f"Successfully minted {ark_count} ARKs"))
