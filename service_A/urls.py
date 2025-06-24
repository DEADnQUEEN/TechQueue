from django.urls import path
from service_A import views
from DjangoProject import settings

urlpatterns = [
    path('<device_id>', views.activate_device, name='activate_view'),
]
