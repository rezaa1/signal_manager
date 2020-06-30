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


    def list(self, request):
        queryset = Signal.objects.filter(owner=request.user).exclude(order_status='Deleted')
        serializer = SignalSerializer(queryset, many=True)
        return Response(serializer.data)



        pass

    def create(self, request):
        pass

    def retrieve(self, request, pk=None):
        pass

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass


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
    queryset = Signal.objects.all()
    serializer_class = SignalSerializer
    def get_search_fields(self, view, request):
        if request.query_params.get('order_id'):
            return ('id',)
        return super(CustomSearchFilter, self).get_search_fields(view, request)
