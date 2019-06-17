import json
from datetime import datetime
from calendar import timegm
from django.http import HttpResponse
from django.utils.http import http_date
from django.middleware.http import ConditionalGetMiddleware
from django.db.models import Max
import django.dispatch
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_walletpass.models import Pass, Registration, Log
from django_walletpass.settings import dwpconfig as WALLETPASS_CONF

FORMAT = '%Y-%m-%d %H:%M:%S'
PASS_REGISTERED = django.dispatch.Signal()
PASS_UNREGISTERED = django.dispatch.Signal()


def get_pass(pass_type_id, serial_number):
    return get_object_or_404(Pass, pass_type_identifier=pass_type_id, serial_number=serial_number)


class RegistrationsViewSet(viewsets.ViewSet):
    """
    Gets the Serial Numbers for Passes Associated with a Device
    """
    permission_classes = (AllowAny, )

    def list(self, request, device_library_id, pass_type_id):
        passes = Pass.objects.filter(
            registrations__device_library_identifier=device_library_id,
            pass_type_identifier=pass_type_id,
        )
        if passes.count() == 0:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        if 'passesUpdatedSince' in request.GET:
            passes = passes.filter(updated_at__gt=datetime.strptime(request.GET['passesUpdatedSince'], FORMAT))

        if passes:
            last_updated = passes.aggregate(Max('updated_at'))['updated_at__max']
            serial_numbers = [p.serial_number for p in passes.filter(updated_at=last_updated).all()]
            response_data = {'lastUpdated': last_updated.strftime(FORMAT), 'serialNumbers': serial_numbers}
            return Response(response_data)

        return Response({}, status=status.HTTP_204_NO_CONTENT)


# TODO: Refactor.
# - Use a ModelViewSet
# - Use auth class
class RegisterPassViewSet(viewsets.ViewSet):
    """
    get: Registers a Device to Receive Push Notifications for a Pass
    destroy: Unregister a Device
    """
    permission_classes = (AllowAny, )

    def create(self, request, device_library_id, pass_type_id, serial_number):

        pass_ = get_pass(pass_type_id, serial_number)
        if request.META.get('HTTP_AUTHORIZATION') != 'ApplePass %s' % pass_.authentication_token:
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)
        registration = Registration.objects.filter(
            device_library_identifier=device_library_id,
            pazz=pass_,
        )
        if registration:
            return Response({}, status=status.HTTP_200_OK)
        body = json.loads(request.body)
        new_registration = Registration(
            device_library_identifier=device_library_id,
            push_token=body['pushToken'],
            pazz=pass_,
        )
        new_registration.save()
        PASS_REGISTERED.send(sender=pass_)
        return Response({}, status=status.HTTP_201_CREATED)

    def destroy(self, request, device_library_id, pass_type_id, serial_number):
        pass_ = get_pass(pass_type_id, serial_number)
        if request.META.get('HTTP_AUTHORIZATION') != 'ApplePass %s' % pass_.authentication_token:
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)
        registration = Registration.objects.filter(
            device_library_identifier=device_library_id,
            pazz=pass_,
        )
        if registration:
            return Response({}, status=status.HTTP_200_OK)
        registration.delete()
        PASS_UNREGISTERED.send(sender=pass_)
        return Response({}, status=status.HTTP_200_OK)


class LatestVersionViewSet(viewsets.ViewSet):
    """
    get: Gets the latest version of a Pass
    """
    permission_classes = (AllowAny, )

    def retrieve(self, request, pass_type_id, serial_number):
        pass_ = get_pass(pass_type_id, serial_number)

        if request.META.get('HTTP_AUTHORIZATION') != 'ApplePass %s' % pass_.authentication_token:
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)

        if WALLETPASS_CONF['STORAGE_HTTP_REDIRECT']:
            return Response({}, status=status.HTTP_302_FOUND, headers={'Location': pass_.data.url})

        response = HttpResponse(pass_.data.read(), content_type='application/vnd.apple.pkpass')
        response['Content-Disposition'] = 'attachment; filename=pass.pkpass'

        response['Last-Modified'] = http_date(timegm(pass_.updated_at.utctimetuple()))
        middleware = ConditionalGetMiddleware()
        return middleware.process_response(request, response)


# TODO: use ModelViewSet
class LogViewSet(viewsets.ViewSet):
    """
    Logs messages from devices
    """
    permission_classes = (AllowAny, )

    def create(self, request):
        json_body = json.loads(request.body)
        for message in json_body['logs']:
            Log(message=message).save()
        return Response({}, status=status.HTTP_200_OK)
