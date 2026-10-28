from datetime import datetime

from django.test import TestCase
from unittest import mock

from apps.attendance.models import PunchEvent
from apps.employees.models import DeviceUserMap, Employee

from .adapters import DeviceError, RawPunch
from .models import Device
from .services import sync_device


class SyncTests(TestCase):
    def setUp(self):
        self.dev = Device.objects.create(name="D1", vendor="zkteco", ip_address="10.0.0.5")
        emp = Employee.objects.create(matricule="E1", first_name="A", last_name="B")
        DeviceUserMap.objects.create(employee=emp, device=self.dev, device_user_id="7")

    def _sync(self, punches=None, exc=None):
        with mock.patch("apps.devices.services.get_adapter") as g:
            if exc:
                g.return_value.fetch_punches.side_effect = exc
            else:
                g.return_value.fetch_punches.return_value = punches
            return sync_device(self.dev)

    def test_idempotent_and_mapped(self):
        p = [RawPunch("7", datetime(2026, 1, 1, 8, 0)), RawPunch("7", datetime(2026, 1, 1, 17, 0))]
        self.assertEqual(self._sync(p).created, 2)
        r = self._sync(p + [RawPunch("9", datetime(2026, 1, 2, 8, 0))])
        self.assertEqual((r.fetched, r.created), (3, 1))
        self.assertEqual(PunchEvent.objects.filter(employee__matricule="E1").count(), 2)

    def test_failure_keeps_data_and_flags_device(self):
        self._sync([RawPunch("7", datetime(2026, 1, 1, 8, 0))])
        r = self._sync(exc=DeviceError("boom", "network"))
        self.assertFalse(r.success)
        self.dev.refresh_from_db()
        self.assertEqual((self.dev.status, self.dev.consecutive_failures, self.dev.events_total), ("disconnected", 1, 1))
        self.assertEqual(PunchEvent.objects.count(), 1)


class ApiTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        from rest_framework.authtoken.models import Token
        self.tok = Token.objects.create(user=User.objects.create_user("u", password="p")).key

    def test_requires_auth_and_creates(self):
        self.assertEqual(self.client.get("/api/devices/").status_code, 401)
        h = {"HTTP_AUTHORIZATION": f"Token {self.tok}"}
        r = self.client.post("/api/devices/", {"name": "X", "vendor": "zkteco", "ip_address": "10.0.0.9", "port": 4370},
                             content_type="application/json", **h)
        self.assertEqual(r.status_code, 201)
        self.assertNotIn("comm_key", r.json())
