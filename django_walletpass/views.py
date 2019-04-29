import json
from datetime import datetime
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import condition
from django.db.models import Max
import django.dispatch
from django.shortcuts import get_object_or_404
from django_walletpass.models import Pass, Registration, Log

FORMAT = '%Y-%m-%d %H:%M:%S'
PASS_REGISTERED = django.dispatch.Signal()
PASS_UNREGISTERED = django.dispatch.Signal()


def registrations(request, device_library_id, pass_type_id):
    """
    Gets the Serial Numbers for Passes Associated with a Device
    """
    passes = Pass.objects.filter(
        registration__device_library_identifier=device_library_id, pass_type_identifier=pass_type_id)
    if passes.count() == 0:
        return HttpResponse(status=404)

    if 'passesUpdatedSince' in request.GET:
        passes = passes.filter(updated_at__gt=datetime.strptime(request.GET['passesUpdatedSince'], FORMAT))

    if passes:
        last_updated = passes.aggregate(Max('updated_at'))['updated_at__max']
        serial_numbers = [p.serial_number for p in passes.filter(updated_at=last_updated).all()]
        response_data = {'lastUpdated': last_updated.strftime(FORMAT), 'serialNumbers': serial_numbers}
        return HttpResponse(json.dumps(response_data), mimetype="application/json")
    return HttpResponse(status=204)


@csrf_exempt
def register_pass(request, device_library_id, pass_type_id, serial_number):
    """
    Registers/Unregisters a Device to Receive Push Notifications for a Pass
    """
    pass_ = get_pass(pass_type_id, serial_number)

    if request.META.get('HTTP_AUTHORIZATION') != 'ApplePass %s' % pass_.authentication_token:
        return HttpResponse(status=401)

    registration = Registration.objects.filter(device_library_identifier=device_library_id, pazz=pass_)

    if request.method == 'POST':
        if registration:
            return HttpResponse(status=200)
        body = json.loads(request.body)
        new_registration = Registration(
            device_library_identifier=device_library_id, push_token=body['pushToken'], pazz=pass_)
        new_registration.save()
        PASS_REGISTERED.send(sender=pass_)
        return HttpResponse(status=201)

    if request.method == 'DELETE':
        registration.delete()
        PASS_UNREGISTERED.send(sender=pass_)
        return HttpResponse(status=200)

    return HttpResponse(status=400)


def latest_pass(_request, pass_type_id, serial_number):
    return get_pass(pass_type_id, serial_number).updated_at


@condition(last_modified_func=latest_pass)
def latest_version(request, pass_type_id, serial_number):
    """
    Gets the latest version of a Pass
    """
    pass_ = get_pass(pass_type_id, serial_number)

    if request.META.get('HTTP_AUTHORIZATION') != 'ApplePass %s' % pass_.authentication_token:
        return HttpResponse(status=401)

    response = HttpResponse(pass_.data.read(), content_type='application/vnd.apple.pkpass')
    response['Content-Disposition'] = 'attachment; filename=pass.pkpass'
    return response


@csrf_exempt
def log(request):
    """
    Logs messages from devices
    """
    json_body = json.loads(request.body)
    for message in json_body['logs']:
        Log(message=message).save()
    return HttpResponse(status=200)


def get_pass(pass_type_id, serial_number):
    return get_object_or_404(Pass, pass_type_identifier=pass_type_id, serial_number=serial_number)
