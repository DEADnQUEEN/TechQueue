from django.urls import path
from service_B import views

urlpatterns = [
    path('<device_id>/', views.async_configure, name='setup_task'),
    path('<device_id>/task/<task_id>/', views.get_task_state, name='task_state'),
]
