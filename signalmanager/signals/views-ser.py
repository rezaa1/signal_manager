from django.contrib.auth.models import User
from rest_framework import generics, permissions, renderers, viewsets
from rest_framework.decorators import api_view, detail_route
from rest_framework.response import Response
from rest_framework.reverse import reverse

from signals.models import Signal
from signals.permissions import IsOwnerOrReadOnly
from signals.serializers import SignalSerializer, UserSerializer


from rest_framework import filters
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from signals.models import Signal
from signals.serializers import SignalSerializer


from rest_framework import status
from rest_framework.decorators import api_view




class SignalViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `highlight` action.
    """
    queryset = Signal.objects.all()
    serializer_class = SignalSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly, )


    @detail_route(renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        signal = self.get_object()
        return Response(signal.highlighted)

    def perform_create(self, serializer):
        print(dir(self))
        serializer.save(owner=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', 'email')

class SignalSearchFilter(filters.SearchFilter):
    def get_search_fields(self, view, request):
        if request.query_params.get('order_id'):
            return ('id',)
        return super(CustomSearchFilter, self).get_search_fields(view, request)
