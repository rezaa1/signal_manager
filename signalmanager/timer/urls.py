from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from timer import views

urlpatterns = [
    path('timenow', views.timenow),
]

urlpatterns = format_suffix_patterns(urlpatterns)

