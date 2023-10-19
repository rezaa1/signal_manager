from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class SignalHookView(APIView):
    """
    List all code signals, or create a new signal.
    """

    def post(self, request):
        update = False
        try:
            signal = Signal.objects.get(owner=request.user, order_id=request.data['order_id'])
            serializer = SignalSerializer(signal, data=request.data)
            update = True
        except Signal.DoesNotExist:
            if request.data.order_size != 0:
                request.data.order_status = "Active"
            serializer = SignalSerializer(data=request.data)

        if serializer.is_valid():
            if update:
                # send_update(request.data, signal)
                if request.data.order_size == 0:
                    request.data.order_status = "Closed"
                order_update = generate_update(request=request.data, data=signal)
                message = generate_message(request=request.data, data=signal)
                serializer.save(owner=request.user)
                manage_channels(signal.id, message, update)
                manage_trades(signal.id, update=order_update)
            else:
                message = generate_message(request=request.data, data=None)
                serializer.save(owner=request.user, standard_symbol=get_standard_symbol(request.data['order_symbol']))
                signal = Signal.objects.get(owner=request.user, order_id=request.data['order_id'])
                manage_channels(signal.id, message, update)
                manage_trades(signal.id)
                # id = send_update(request.data)
                # serializer.save(owner=request.user, message_id=id)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

