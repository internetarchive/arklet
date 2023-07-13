"""Django Admin command to mint a test ARK 

"""

from django.core.management.base import BaseCommand

from ark.models import Ark, Naan
from ark.utils import generate_noid


class Command(BaseCommand):
    """Mint ark_count ARKs for the given naan and shoulder."""

    help = "Mint ARKs in bulk"

    def add_arguments(self, parser):
        parser.add_argument("naan", type=int)
        parser.add_argument("shoulder", type=str)

    def handle(self, *args, **options):
        naan_id = options["naan"]
        naan = Naan.objects.get(pk=options["naan"])
        if not naan:
            print('minting naan')
            naan = Naan(naan=options['naan'])
            naan.save()

        shoulder = options["shoulder"]

        arkstr = f"{naan_id}{shoulder}teststr"
        print(f"minting {arkstr}")
        a = Ark(
                ark=arkstr,
                naan=naan,
                shoulder=shoulder,
                title = "Bibliographie zur kunstgeschichtlichen Literatur in ost- und südosteuropäischen Zeitschriften.",
                type = 'Book',
                rights = 'rights statement',
                identifier = ' LC : 76643184 OCLC : (OCoLC)191719045',
                format = 'Hardcover',
                relation = 'https://ark.frick.org/ark:37624/an1abc123',
                source = 'https://yamz.net/term/ark/h3886',
                url="https://library.frick.org/permalink/01NYA_INST/1qqhid8/alma991000000019707141",
                metadata="Issues for 1990- have title: Bibliographie zur kunstgeschichtlichen Literatur- in ost-, mittelost- und südosteuropäischen Zeitschriften."
            )
        a.save()
