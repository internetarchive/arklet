import json
import logging

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseNotAllowed,
    HttpResponseRedirect,
    HttpResponseServerError,
    JsonResponse,
)
from django.views.decorators.csrf import csrf_exempt

from ark.forms import MintArkForm, UpdateArkForm
from ark.models import Ark, Naan
from ark.utils import generate_noid, noid_check_digit, parse_ark

logger = logging.getLogger(__name__)


@csrf_exempt
def mint_ark(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(permitted_methods=["POST"])

    try:
        unsafe_mint_request = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, TypeError) as e:
        return HttpResponseBadRequest(e)

    mint_request = MintArkForm(unsafe_mint_request)

    if not mint_request.is_valid():
        return JsonResponse(mint_request.errors, status=400)

    # TODO: get rid of UUID for key
    # TODO: hash the keys and only show on creation
    bearer_token = request.META.get("HTTP_AUTHORIZATION")
    if not bearer_token:
        return HttpResponseForbidden()

    key = bearer_token.split()[-1]

    try:
        authorized_naan = Naan.objects.get(key__key=key)
    except Naan.DoesNotExist:
        return HttpResponseForbidden()
    except ValidationError as e:  # probably an invalid key
        return HttpResponseBadRequest(e)

    naan = mint_request.cleaned_data["naan"]
    shoulder = mint_request.cleaned_data["shoulder"]
    url = mint_request.cleaned_data["url"]
    metadata = mint_request.cleaned_data["metadata"]
    commitment = mint_request.cleaned_data["commitment"]

    if authorized_naan.naan != naan:
        return HttpResponseForbidden()

    ark, collisions = None, 0
    for _ in range(10):
        noid = generate_noid(8)
        base_ark_string = f"{naan}{shoulder}{noid}"
        check_digit = noid_check_digit(base_ark_string)
        ark_string = f"{base_ark_string}{check_digit}"
        try:
            ark = Ark.objects.create(
                ark=ark_string,
                naan=authorized_naan,
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

    if not ark:
        msg = f"Gave up creating ark after {collisions} collision(s)"
        logger.error(msg)
        return HttpResponseServerError(msg)
    if ark and collisions > 0:
        logger.warning("Ark created after %d collision(s)", collisions)

    return JsonResponse({"ark": str(ark)})


@csrf_exempt
def update_ark(request):
    if request.method != "PUT":
        return HttpResponseNotAllowed(permitted_methods=["PUT"])

    try:
        unsafe_update_request = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, TypeError) as e:
        return HttpResponseBadRequest(e)

    # TODO: test input data with wrong structure
    update_request = UpdateArkForm(unsafe_update_request)

    if not update_request.is_valid():
        return JsonResponse(update_request.errors, status=400)

    # TODO: get rid of UUID for key
    # TODO: hash the keys and only show on creation
    bearer_token = request.META.get("HTTP_AUTHORIZATION")
    if not bearer_token:
        return HttpResponseForbidden()

    key = bearer_token.split()[-1]

    try:
        # TODO: is key valid enough to pass here?
        authorized_naan = Naan.objects.get(key__key=key)
    except Naan.DoesNotExist:
        return HttpResponseForbidden()
    except ValidationError as e:
        return HttpResponseBadRequest(e)

    ark = update_request.cleaned_data["ark"]
    url = update_request.cleaned_data["url"]
    metadata = update_request.cleaned_data["metadata"]
    commitment = update_request.cleaned_data["commitment"]

    _, naan, assigned_name = parse_ark(ark)

    if authorized_naan.naan != naan:
        return HttpResponseForbidden()

    try:
        ark = Ark.objects.get(ark=f"{naan}/{assigned_name}")
    except Ark.DoesNotExist:
        raise Http404

    ark.url = url
    ark.metadata = metadata
    ark.commitment = commitment
    ark.save()

    return HttpResponse()


def resolve_ark(request, ark: str):
    # TODO: maybe just parse the ark in the urls.py re_path
    try:
        _, naan, assigned_name = parse_ark(ark)
    except ValueError as e:
        return HttpResponseBadRequest(e)
    try:
        ark_obj = Ark.objects.get(ark=f"{naan}/{assigned_name}")
        if not ark_obj.url:
            # TODO: return a template page for an ARK in progress
            raise Http404
        return HttpResponseRedirect(ark_obj.url)
    except Ark.DoesNotExist:
        try:
            naan_obj = Naan.objects.get(naan=naan)
            return HttpResponseRedirect(
                f"{naan_obj.url}/ark:/{naan_obj.naan}/{assigned_name}"
            )
        except Naan.DoesNotExist:
            resolver = "https://n2t.net"
            # TODO: more robust resolver URL creation
            return HttpResponseRedirect(f"{resolver}/ark:/{naan}/{assigned_name}")
