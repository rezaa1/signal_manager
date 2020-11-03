from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from signals import views
from django.urls import path
from signals import views


from rest_framework.authtoken.views import ObtainAuthToken



# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'signals', views.SignalViewSet)
router.register(r'users', views.UserViewSet)


# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls))
]
urlpatterns += [
    url(r'^get-user-auth-token/', ObtainAuthToken, name='get_user_auth_token')
]


urlpatterns += [
    path('signals/search/', views.SignalSearchFilter),
]


