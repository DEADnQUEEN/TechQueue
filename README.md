# Для запуска основного приложения необходимо:
```
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
python .\manage.py makemigrations
python .\manage.py migrate
```
## Для отправки запросов необходимо добавить устройство:
```
python .\manage.py shell # Подключение к консоли
from service_A.models import Device
d = Device(id='deviceId', username='username', password='password')
d.save()
exit()
```
## Для запуска сервера:
```
python .\manage.py runserver localhost:8000
```
## RabbitMQ 
обработчик работает в фоне, чтобы включить его и чтобы он обрабатывал запросы необходимо запустить его в фоне
```
python .\manage.py worker
```
>[!warning] 
>Так как у сервиса А и сервиса Б один и тот же начальный Endpoint, то для того чтобы разделить на синхронный и асинхронный вариант-ы, в начало пути для сервиса Б было добавлено: **async/**

#Схемы работы
## Service A
![Screenshot 2025-06-24 081948](https://github.com/user-attachments/assets/edacc1ce-51b9-44a2-85fb-c3d60b00d62c)
## Service B
### Получение статуса задачи
![Screenshot 2025-06-24 081835](https://github.com/user-attachments/assets/172c2f32-5af5-45fd-a15e-96dc523d65de)
### Отправка запроса на конфигурацию
![Screenshot 2025-06-24 082202](https://github.com/user-attachments/assets/1e75ca66-4579-4003-95d1-ce9c81873b01)
## Worker (RabbitMQ обработчик)
![Screenshot 2025-06-24 082550](https://github.com/user-attachments/assets/8e692e5e-042e-452c-bedb-62c1855614f5)
