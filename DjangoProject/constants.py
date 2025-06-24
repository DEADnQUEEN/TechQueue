from django.http.response import JsonResponse
import pika
import json

PIKA_PARAMS = pika.ConnectionParameters(host='localhost')
MAX_USERNAME_LENGTH = 50
MAX_PASSWORD_LENGTH = 50
MAX_ID_SIZE = 100

TASK_CODE_TAG = 'taskId'


IN_PROGRESS_QUEUE_CODE = 204
DONE_QUEUE_CODE = 200
QUEUE_NAMES = {
    IN_PROGRESS_QUEUE_CODE: 'in_progress_config_queue',
    DONE_QUEUE_CODE: 'done_config_queue',
    '*': '*'
}
QUEUE_MESSAGES = {
    IN_PROGRESS_QUEUE_CODE: 'In progress',
    DONE_QUEUE_CODE: 'Completed',
}


def prepare_json_response(code, message, **kwargs):
    return JsonResponse(
        {
            'code': code,
            'message': message,
            **kwargs,
        }
    )

def prepare_queue_message(task_code, **kwargs):
    return json.dumps(
        {
            'code': task_code,
            **kwargs,
        }
    )

def get_queue(code, task=None):
    return f"{QUEUE_NAMES[code]}.{task.id if task else '*'}"
