import re
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import QuerySet
from DjangoProject import constants


class SetupError(Exception):
    pass


def validator(val):
    if re.match('^[a-zA-Z0-9]{6,}$', val):
        raise ValidationError('Invalid value')


class Interface(models.Model):
    @classmethod
    def setup_interfaces(cls, interface_ids: list) -> QuerySet:
        exists = [
            instance.id
            for instance in cls.objects.filter(id__in=interface_ids)
        ]

        not_exists = [interface_id for interface_id in interface_ids if interface_id not in exists]

        for not_exist in not_exists:
            instance = cls(id=not_exist)
            instance.save()

        return cls.objects.filter(id__in=interface_ids)

    @classmethod
    async def asetup_interfaces(cls, interface_ids: list) -> QuerySet:
        exists = [
            instance.id
            for instance in cls.objects.filter(id__in=interface_ids)
        ]

        not_exists = [interface_id for interface_id in interface_ids if interface_id not in exists]

        for not_exist in not_exists:
            instance = cls(id=not_exist)
            await instance.asave()

        return cls.objects.filter(id__in=interface_ids)

    class Meta:
        db_table = 'interfaces'
        verbose_name = 'Интерфейс'
        verbose_name_plural = "Интерфейсы"


class Device(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=constants.MAX_ID_SIZE,
        validators=[
            validator,
        ]
    )

    username = models.CharField(
        max_length=constants.MAX_USERNAME_LENGTH,
        verbose_name='Имя пользователя',
    )
    password = models.CharField(
        max_length=constants.MAX_PASSWORD_LENGTH,
        verbose_name="пароль",
    )

    vlan = models.IntegerField(
        null=True,
        verbose_name='VLAN'
    )

    interfaces = models.ManyToManyField(
        Interface,
        verbose_name="Интерфейсы",
        related_name='devices',
    )

    def setup_from_params(self, params: dict[str: str | int | list[str]]) -> None:
        if not ('username' in params and 'password' in params):
            raise SetupError

        self.username = params['username']
        self.password = params['password']
        self.vlan = params['vlan'] if 'vlan' in params else None
        self.save()

        for interface in Interface.objects.filter(id__in=params['interfaces']):
            self.interfaces.add(interface)

        self.save()

    async def asetup_from_params(self, params: dict[str: str | int | list[str]]) -> None:
        if not ('username' in params and 'password' in params):
            raise SetupError

        self.username = params['username']
        self.password = params['password']
        self.vlan = params['vlan'] if 'vlan' in params else None
        await self.asave()

        async for interface in Interface.objects.filter(id__in=params['interfaces']):
            self.interfaces.add(interface)

        await self.asave()

    class Meta:
        db_table = 'devices'
        verbose_name = 'Устройство'
        verbose_name_plural = "Устройства"


class Task(models.Model):
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name="Устройство"
    )
    parameters = models.JSONField(
        default=dict,
        blank=True,
    )
    procedure_time = models.IntegerField(
        verbose_name='Время конфигурирования',
        default=0
    )

    class Meta:
        db_table = "task"
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'