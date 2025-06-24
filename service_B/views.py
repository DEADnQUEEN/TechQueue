import json
import pika
from DjangoProject import constants, rabbit
import http
from DjangoProject.constants import QUEUE_MESSAGES
from service_A import models
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt


def check_queue(channel, queue):
    channel.queue_declare(queue=queue, durable=True)
    method, properties, body = channel.basic_get(queue)
    if not method or not properties or not body:
        return
    json_data = json.loads(body)

    return json_data[constants.TASK_CODE_TAG]


def check_message(task: models.Task) -> int | None:
    """
    Получение сообщения из очереди
    Если сообщение есть в очереди на обработку, то будет код :param 204:
    Если сообщение есть в очереди готовых, то будет код :param 200:
    :param task:
    :return:
    """
    with pika.BlockingConnection(constants.PIKA_PARAMS) as connection:
        with connection.channel() as channel:
            answer = check_queue(
                channel,
                constants.get_queue(
                    constants.IN_PROGRESS_QUEUE_CODE, task
                )
            )
            if answer:
                return answer

            return check_queue(
                channel,
                constants.get_queue(
                    constants.DONE_QUEUE_CODE, task
                )
            )

@require_GET
def get_task_state(request, device_id, task_id):
    try:
        device = models.Device.objects.get(id=device_id)
    except models.Device.DoesNotExist:
        return constants.prepare_json_response(
            code=http.HTTPStatus.NOT_FOUND,
            message="The requested equipment is not found",
        )

    try:
        task = models.Task.objects.get(id=task_id)
    except models.Task.DoesNotExist:
        return constants.prepare_json_response(
            code=http.HTTPStatus.NOT_FOUND,
            message="The requested task is not found",
        )

    if task.device != device:
        return constants.prepare_json_response(
            code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
            message="Internal provisioning exception",
        )

    code = check_message(task)
    if not code:
        return constants.prepare_json_response(
            code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
            message="Internal provisioning exception",
        )

    return constants.prepare_json_response(
        code=code,
        message=QUEUE_MESSAGES[code],
    )

@require_POST
@csrf_exempt
async def async_configure(request, device_id):
    try:
        device = await models.Device.objects.aget(id=device_id)
    except models.Device.DoesNotExist:
        return constants.prepare_json_response(
            code=http.HTTPStatus.NOT_FOUND,
            message="The requested equipment is not found",
        )

    try:
        json_data = json.loads(request.body)
    except json.decoder.JSONDecodeError or models.SetupError:
        return constants.prepare_json_response(
            code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
            message='Internal provisioning exception'
        )

    task = await models.Task.objects.acreate(
        device=device,
        parameters=json_data['parameters'],
        procedure_time=json_data['timeoutInSeconds'],
    )
    await task.asave()

    try:
        await device.asetup_from_params(json_data['parameters'])
    except models.SetupError:
        return constants.prepare_json_response(
            code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
            message='Internal provisioning exception'
        )

    rabbit.enqueue_task(task=task)

    return constants.prepare_json_response(
        code=http.HTTPStatus.OK,
        message="Success",
        taskId=task.id,
    )



