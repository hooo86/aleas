from rest_framework import viewsets

from .models import PunchEvent
from .serializers import PunchEventSerializer


class PunchEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PunchEvent.objects.select_related("device", "employee")
    serializer_class = PunchEventSerializer
    filterset_fields = {"device": ["exact"], "employee": ["exact"], "timestamp": ["gte", "lte"]}
    search_fields = ["device_user_id", "employee__matricule", "employee__last_name"]
    ordering_fields = ["timestamp"]
