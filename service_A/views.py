import time
import http
import json
from DjangoProject import constants
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from  service_A import models


@require_POST
@csrf_exempt
def activate_device(request, device_id):
    try:
        device = models.Device.objects.get(id=device_id)
    except models.Device.DoesNotExist:
        return constants.prepare_json_response(
            code=http.HTTPStatus.NOT_FOUND,
            message='The requested equipment is not found'
        )

    try:
        json_data = json.loads(request.body)
    except json.decoder.JSONDecodeError:
        return constants.prepare_json_response(
            code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
            message='Internal provisioning exception'
        )

    task = models.Task(
        device=device,
        parameters=json_data['parameters'],
        procedure_time=json_data['timeoutInSeconds'],
    )
    task.save()

    try:
        device.setup_from_params(json_data['parameters'])
    except models.SetupError:
        return constants.prepare_json_response(
            code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
            message='Internal provisioning exception'
        )

    time.sleep(json_data['timeoutInSeconds'])

    return constants.prepare_json_response(
        code=http.HTTPStatus.OK,
        message='success',
    )




