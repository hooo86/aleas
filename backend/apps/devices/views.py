from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Device, SyncLog
from .serializers import DeviceSerializer, SyncLogSerializer
from .services import diagnose
from .tasks import sync_device_task


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    search_fields = ["name", "ip_address", "serial_number", "model"]
    filterset_fields = ["vendor", "status", "enabled"]

    @action(detail=True, methods=["post"])
    def test_connection(self, request, pk=None):
        return Response(diagnose(self.get_object()))

    @action(detail=True, methods=["post"])
    def sync(self, request, pk=None):
        sync_device_task.delay(self.get_object().pk, SyncLog.Trigger.MANUAL)
        return Response({"queued": True}, status=202)


class SyncLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SyncLog.objects.select_related("device")
    serializer_class = SyncLogSerializer
    filterset_fields = ["device", "success", "trigger"]
