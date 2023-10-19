from django.urls import path
from .views import SignalHookView

urlpatterns = [
    path('hook', SignalHookView.as_view(), name='signal_hook'),
]
