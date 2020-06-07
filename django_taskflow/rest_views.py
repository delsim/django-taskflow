"""
DRF views to provide endpoints
"""


from rest_framework import serializers


class TicketArgumentSerializer(serializers.Serializer):

    workflow = serializers.SlugField()
    state = serializers.JSONField()
