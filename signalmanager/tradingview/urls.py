from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from tradingview import views

from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.permissions import AllowAny


urlpatterns = [
    path('tv/hook', authentication_classes([])(permission_classes([AllowAny])(views.signal_hook)).as_view())
]


urlpatterns = format_suffix_patterns(urlpatterns)
