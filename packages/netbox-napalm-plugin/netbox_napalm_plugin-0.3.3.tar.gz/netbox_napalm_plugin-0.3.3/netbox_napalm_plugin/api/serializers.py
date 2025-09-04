from dcim.api.serializers_.platforms import PlatformSerializer
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers

from netbox_napalm_plugin.models import NapalmPlatformConfig


class NapalmPlatformConfigSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_napalm_plugin-api:napalmplatformconfig-detail"
    )
    platform = PlatformSerializer(nested=True)

    class Meta:
        model = NapalmPlatformConfig
        fields = [
            "id",
            "url",
            "platform",
            "napalm_driver",
            "napalm_args",
            "tags",
            "created",
            "last_updated",
        ]


class DeviceNAPALMSerializer(serializers.Serializer):
    method = serializers.JSONField()
