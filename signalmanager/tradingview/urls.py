from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from tradingview import views

from rest_framework.decorators import permission_classes, authentication_classes, api_view
from rest_framework.permissions import AllowAny


urlpatterns = [
    path('hook', api_view(['POST'])(authentication_classes([])(permission_classes([AllowAny])(views.signal_hook))))

]


urlpatterns = format_suffix_patterns(urlpatterns)
