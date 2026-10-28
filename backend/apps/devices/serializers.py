from rest_framework import serializers

from .models import Device, SyncLog


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = "__all__"
        read_only_fields = ["status", "last_error", "last_seen_at", "last_sync_at", "last_sync_ok",
                            "events_total", "consecutive_failures"]
        extra_kwargs = {"comm_key": {"write_only": True}}


class SyncLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncLog
        fields = "__all__"
