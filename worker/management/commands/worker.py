import json
import requests
from django.shortcuts import reverse
from service_A import models
from DjangoProject import rabbit, constants
from django.core.management.base import BaseCommand


def callback(channel, method, _, body):
    json_data = json.loads(body)
    task = models.Task.objects.get(id=json_data['taskId'])
    requests.post(
        url=f'http://localhost:8000{reverse(
            'activate_view',
            args=(
                task.device.id,
            )
        )}',
        data={
            'timeoutInSeconds': json_data['timeoutInSeconds'],
            'parameters': json_data['parameters'],
        }
    )

    channel.basic_ack(delivery_tag=method.delivery_tag)

    rabbit.enqueue_task(
        task=task,
        code=constants.DONE_QUEUE_CODE
    )


class Command(BaseCommand):
    def handle(self, *args, **options):
        rabbit.setup_consumer(
            constants.IN_PROGRESS_QUEUE_CODE,
            callback=callback
        )

