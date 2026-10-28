from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.attendance.views import PunchEventViewSet
from apps.devices.views import DeviceViewSet, SyncLogViewSet
from apps.employees.views import EmployeeViewSet

router = DefaultRouter()
router.register("devices", DeviceViewSet)
router.register("sync-logs", SyncLogViewSet)
router.register("employees", EmployeeViewSet)
router.register("punches", PunchEventViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
]
