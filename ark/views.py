import json
import logging

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
from ark.models import APIKey, Ark, Naan
from ark.utils import parse_ark

logger = logging.getLogger(__name__)


def authorize(request) -> Naan:
    bearer_token = request.headers.get("Authorization")
    plain_key = bearer_token.split()[-1]
    try:
        authorized_naan = Naan.objects.get(key__key=plain_key)
    except Naan.DoesNotExist:
        api_key = APIKey.objects.get_by_plain_key(plain_key)
        authorized_naan = api_key.naan
    return authorized_naan


@csrf_exempt
def mint_ark(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(permitted_methods=["POST"])

    # Check if request has an authorized NAAN
    try:
        authorized_naan = authorize(request)
    except Exception:
        return HttpResponseForbidden()

    # Validate POST
    try:
        unsafe_mint_request = json.loads(request.body.decode("utf-8"))
        mint_request = MintArkForm(unsafe_mint_request)
        if not mint_request.is_valid():
            return JsonResponse(mint_request.errors, status=400)
    except (json.JSONDecodeError, TypeError):
        return HttpResponseBadRequest()

    # Check NAAN is authorized to mint ARK for NAAN
    naan = mint_request.cleaned_data["naan"]
    if authorized_naan.naan != naan:
        return HttpResponseForbidden()

    # Mint the ARK
    shoulder = mint_request.cleaned_data["shoulder"]
    url = mint_request.cleaned_data["url"]
    metadata = mint_request.cleaned_data["metadata"]
    commitment = mint_request.cleaned_data["commitment"]
    ark, collisions = Ark.objects.mint(
        authorized_naan, shoulder, url, metadata, commitment
    )

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

    # Check if request has an authorized NAAN
    try:
        authorized_naan = authorize(request)
    except Exception:
        return HttpResponseForbidden()

    # Validate PUT
    try:
        unsafe_update_request = json.loads(request.body.decode("utf-8"))
        update_request = UpdateArkForm(unsafe_update_request)
        if not update_request.is_valid():
            return JsonResponse(update_request.errors, status=400)
    except (json.JSONDecodeError, TypeError):
        return HttpResponseBadRequest()

    ark = update_request.cleaned_data["ark"]
    url = update_request.cleaned_data["url"]
    metadata = update_request.cleaned_data["metadata"]
    commitment = update_request.cleaned_data["commitment"]

    _, naan, assigned_name = parse_ark(ark)

    # Check NAAN is authorized to update this ARK
    if authorized_naan.naan != naan:
        return HttpResponseForbidden()

    # Update the ARK
    try:
        ark = Ark.objects.select_for_update(ark=f"{naan}/{assigned_name}")
    except Ark.DoesNotExist:
        raise Http404

    ark.url = url
    ark.metadata = metadata
    ark.commitment = commitment
    ark.save()

    return HttpResponse()


def resolve_ark(request, ark: str):
    try:
        _, naan, assigned_name = parse_ark(ark)
    except ValueError as e:
        logger.warning("Failed to parse ark %s with error %s", ark, e, exc_info=True)
        return HttpResponseBadRequest()
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
