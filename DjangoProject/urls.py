from django.urls import path, include

urlpatterns = [
    path('api/v1/equipment/cpe/', include('service_A.urls')),
    path('async/api/v1/equipment/cpe/', include('service_B.urls')),
]
