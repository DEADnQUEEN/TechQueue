from django.apps import AppConfig
import types


class Service1Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'service_A'

