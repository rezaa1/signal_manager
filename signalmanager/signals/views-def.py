from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from signals.models import Signal
from signals.serializers import SignalSerializer


@api_view(['GET', 'POST'])
def signal_list(request):
    """
    List all code signals, or create a new signal.
    """
    if request.method == 'GET':
        signals = Signal.objects.all()
        serializer = SignalSerializer(signals, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        try:
            signal = Signal.objects.get(order_id=request.data['order_id'])
            serializer = SignalSerializer(signal, data=request.data)
            print("update")
        except Signal.DoesNotExist:
            serializer = SignalSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def signal_detail(request, pk):
    """
    Retrieve, update or delete a code signal.
    """
    try:
        signal = Signal.objects.get(pk=pk)
    except Signal.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SignalSerializer(signal)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = SignalSerializer(signal, data=request.data)
        if serializer.is_valid():
            serializer.save(owner=self.request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        signal.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

